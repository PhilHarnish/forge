import ast
import re
import textwrap

import astor

from data.logic import _ast_factory

_HEADER = ast.parse("""
from data.logic.dsl import *
dimensions = DimensionFactory()
model = Model(dimensions)
""").body


_BOOL_TO_BIN_OP_MAP = {
  ast.Or: ast.BitXor,
  ast.And: ast.BitAnd,
}


_REFERENCE_TYPES = (
  ast.Name,
  ast.Str,
  ast.Num,
)


_CONSTRAINT_TYPES = (
  ast.BinOp,
  # NB: Do not add ast.BoolOp: the "or" and "and" operators cannot be overriden
  # and must be converted to | and &.
  ast.Call,
  ast.Compare,
)


_COMMENT_REGEX = re.compile(r'^(\s*)(#.*)$')


_DIMENSION_DEFINITION_OPERATORS = (
  ast.LtE,
  ast.In,
)


def transform(program):
  cleaned = textwrap.dedent(program.strip('\n'))
  lines = cleaned.split('\n')
  for i, line in enumerate(lines):
    match = _COMMENT_REGEX.match(line)
    if match and match.groups():
      lines[i] = repr(match.groups()[1])
  visited = _GrammarTransformer().visit(ast.parse('\n'.join(lines)))
  ast.fix_missing_locations(visited)
  return visited


class _GrammarTransformer(ast.NodeTransformer):
  def __init__(self):
    super(_GrammarTransformer, self).__init__()
    self._references = {}

  def _register_references(self, *references):
    for reference in references:
      canonical_reference_name = _canonical_reference_name(reference)
      self._references[canonical_reference_name] = ast.Name(
          id=canonical_reference_name,
          ctx=ast.Load(),
      )

  def visit_BoolOp(self, node):
    self.generic_visit(node)
    values = node.values
    op = _BOOL_TO_BIN_OP_MAP[type(node.op)]()
    left, right, *remainder = values
    node = ast.BinOp(
        left=left,
        op=op,
        right=right,
    )
    for right in remainder:
      node = ast.BinOp(
          left=node,
          op=op,
          right=right,
      )
    return node

  def visit_Compare(self, node):
    if len(node.ops) == 1:
      return self.generic_visit(node)
    exprs = []
    last = node.left
    comparators = node.comparators
    for op, right in zip(node.ops, comparators):
      exprs.append(ast.Compare(
          left=last,
          ops=[op],
          comparators=[right],
      ))
      last = right
    return self.visit(ast.Tuple(
        elts=exprs,
        ctx=ast.Load(),
    ))

  def visit_Expr(self, node):
    # This may be a dimensions definition.
    value = node.value
    dimensions = _dimension_definitions(value)
    if not dimensions:
      return self.generic_visit(node)
    elif len(dimensions) == 1:
      dimension, values = next(iter(dimensions.items()))
      targets = []
      try:
        # Treat "values" like an iterable.
        self._register_references(dimension, *values)
        targets.append(_dimension_target_tuple(values))
      except TypeError:
        # Otherwise assume "values" cannot be unpacked.
        self._register_references(dimension)
      targets.append(_dimension_target_dimension(dimension))
      node = ast.Assign(
          targets=targets,
          value=_dimension_value(dimension, values),
      )
      return node
    _fail(node)

  def visit_For(self, node):
    node.target = self.visit(node.target)
    node.iter = self.visit(node.iter)
    body = []
    for expr in node.body:
      body.append(_constrain_expr(self.visit(expr)))
    node.body = body
    orelse = []
    for expr in node.orelse:
      orelse.append(_constrain_expr(self.visit(expr)))
    node.orelse = orelse
    return node

  def visit_GeneratorExp(self, node):
    if len(node.generators) > 1:
      _fail(node, msg='Generators with multiple comprehensions unsupported')
    if not isinstance(node.generators[0], ast.comprehension):
      raise _fail(node)
    generator = self.visit(node.generators[0])
    if not generator.ifs:
      return self.generic_visit(node)
    if len(generator.ifs) > 1:
      _fail(node, msg='Only one generator conditional supported')
    condition = generator.ifs[0]
    generator.ifs.clear()
    node.elt = ast.Compare(
        left=condition,
        ops=[ast.LtE()],
        comparators=[self.visit(node.elt)],
    )
    return node

  def visit_If(self, node):
    """Converts "if A: B" to "A <= B"."""
    if len(node.body) == 0:
      _fail(node, msg='If statement missing body expressions')
    test = self.visit(node.test)
    body = node.body
    orelse = node.orelse
    assignments, body, orelse = _collect_conditional_assignments(
        test, body, orelse)
    constraints, body, orelse = _collect_conditional_constraints(
        test, body, orelse)
    if body or orelse:
      remaining = ast.If(test=node.test, body=body, orelse=orelse)
      _fail(remaining, msg='if statement expressions unconverted')
    result = []
    for assignment in assignments:
      result.append(self.visit(assignment))
    for constraint in constraints:
      result.append(_constrain_expr(self.visit(constraint)))
    return ast.If(
        test=ast.Str(s=astor.to_source(node.test).replace('\n', ' ').strip()),
        body=result,
        orelse=[],
    )

  def visit_Name(self, node):
    canonical_reference_name = _canonical_reference_name(node.id)
    if canonical_reference_name in self._references:
      return self._references[canonical_reference_name]
    return self.generic_visit(node)

  def visit_Module(self, node):
    body = _HEADER.copy()
    for expr in node.body:
      result = self.visit(expr)
      # Unwind multiple expressions.
      if isinstance(result, ast.Expr) and isinstance(result.value, ast.Tuple):
        for child in result.value.elts:
          body.append(_constrain_expr(ast.Expr(value=child)))
      else:
        body.append(_constrain_expr(result))
    node.body = body
    return node

  def visit_Str(self, node):
    canonical_reference_name = _canonical_reference_name(node.s)
    if canonical_reference_name in self._references:
      return self._references[canonical_reference_name]
    return self.generic_visit(node)


def _fail(node, msg='Visit error'):
  try:
    raise NotImplementedError('%s (in ast.%s). Source:\n\t\t\t%s' % (
      msg, node.__class__.__name__, astor.to_source(node)))
  except AttributeError:  # Astor was unable to convert the source.
    raise NotImplementedError('%s (in ast.%s).' % (
      msg, node.__class__.__name__))


def _canonical_reference_name(value):
  if isinstance(value, str):
    return value.replace(' ', '_').replace('-', '_').lower()
  return '_%s' % value


def _constrain_expr(node):
  if isinstance(node, ast.Expr):
    node.value = _constrain_comparison(node.value)
  return node


def _constrain_comparison(node):
  if not isinstance(node, _CONSTRAINT_TYPES):
    return node
  return ast.Call(
      func=ast.Name(
          id='model',
          ctx=ast.Load(),
      ),
      args=[node],
      keywords=[],
  )


def _dimension_definitions(node):
  # a <= {1, 2, 3} style OR a in {1, 2, 3} style.
  compare_match = (
      isinstance(node, ast.Compare) and
      isinstance(node.left, ast.Name) and
      len(node.ops) == 1 and
      isinstance(node.ops[0], _DIMENSION_DEFINITION_OPERATORS) and
      len(node.comparators) == 1
  )
  if not compare_match:
    return None
  dimension = node.left.id
  comparator = node.comparators[0]
  if isinstance(comparator, ast.Set):
    values = comparator.elts
    if not all(isinstance(value, _REFERENCE_TYPES) for value in values):
      return None
    return {
      dimension: [_dimension_name(value) for value in values]
    }
  elif isinstance(comparator, ast.Call):
    return {
      dimension: comparator,
    }


def _dimension_name(node):
  if isinstance(node, ast.Name):
    return node.id
  elif isinstance(node, ast.Str):
    return node.s
  elif isinstance(node, ast.Num):
    return node.n
  _fail(node, msg='Unable to identify dimension node name')


def _dimension_target_tuple(values):
  targets = []
  for value in values:
    name = _canonical_reference_name(value)
    targets.append(ast.Name(
        id=name,
        ctx=ast.Store(),
    ))
  return ast.Tuple(
      elts=targets,
      ctx=ast.Store(),
  )


def _dimension_target_dimension(dimension):
  return ast.Name(id=dimension, ctx=ast.Store())


def _dimension_value(dimension, values):
  return ast.Call(
      func=ast.Name(
          id='dimensions',
          ctx=ast.Load(),
      ),
      args=[],
      keywords=[
        ast.keyword(
            arg=dimension,
            value=_ast_factory.coerce_value(values),
        )
      ],
  )


def _combine_expressions(body):
  exprs = []
  remaining = []
  for expr in body:
    if isinstance(expr, ast.Expr):
      exprs.append(expr)
    else:
      remaining.append(expr)
  if len(exprs) == 0:
    converted = None
  elif len(exprs) == 1:
    # Solitary expressions can be simply returned.
    converted = exprs[0].value
  else:
    # Multiple expressions should be AND'd.
    converted = ast.BoolOp(
        op=ast.And(),
        values=[
          expr.value for expr in exprs
        ]
    )
  return converted, remaining


def _collect_conditional_assignments(condition, body, orelse):
  """Produces x = A * valueA + !A * notValueA."""
  assign_body, remaining_body = _collect_assignments(body)
  assign_orelse, remaining_orelse = _collect_assignments(orelse)
  assert assign_body.keys() == assign_orelse.keys()
  result = []
  for key in assign_body.keys():
    body_value = assign_body[key]
    orelse_value = assign_orelse[key]
    body_conditional_value = _conditional_value_if_bool(
        condition, body_value, True)
    orelse_conditional_value = _conditional_value_if_bool(
        condition, orelse_value, False)
    value_combined = ast.BinOp(
        left=body_conditional_value,
        op=ast.Add(),
        right=orelse_conditional_value,
    )
    result.append(ast.Assign(
        targets=[ast.Name(id=key, ctx=ast.Store())],
        value=value_combined,
    ))
  return result, remaining_body, remaining_orelse


def _collect_assignments(collection):
  assign = {}
  remaining = []
  for expr in collection:
    if isinstance(expr, ast.Assign):
      if len(expr.targets) != 1:
        _fail(expr, 'Multiple conditional assignments unsupported')
      assign[expr.targets[0].id] = expr.value
    else:
      remaining.append(expr)
  return assign, remaining


def _collect_conditional_constraints(condition, body, orelse):
  """Produces model(ifA <= thenB), model(ifNotA + thenB >= 1)."""
  body_implication, remaining_body = _combine_expressions(body)
  result = []
  if body_implication:
    result.append(
        ast.Expr(
            value=ast.Compare(
                left=condition,
                ops=[ast.LtE()],
                comparators=[body_implication],
            )
        )
    )
  if orelse:
    # Convert "else: C" into "A + C >= 1".
    orelse_implication, remaining_orelse = _combine_expressions(orelse)
    if orelse_implication:
      result.append(
          ast.Expr(
              ast.Compare(
                  left=ast.BinOp(
                      left=condition,
                      op=ast.Add(),
                      right=orelse_implication,
                  ),
                  ops=[ast.GtE()],
                  comparators=[ast.Num(n=1)],
              )
          )
      )
  else:
    remaining_orelse = orelse
  return result, remaining_body, remaining_orelse


def _conditional_value_if_bool(condition, value, boolean):
  return ast.BinOp(
      left=ast.Compare(
          left=condition,
          ops=[ast.Eq()],
          comparators=[ast.NameConstant(value=boolean)],
      ),
      op=ast.Mult(),
      right=value,
  )

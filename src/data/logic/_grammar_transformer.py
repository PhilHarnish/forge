import ast
import collections
import itertools
import re
import textwrap

import astor

from data.logic import _ast_factory, _util

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
  # NB: Do not add ast.BoolOp: the "or" and "and" operators cannot be overridden
  # and must be converted to | and &.
  ast.Call,
  ast.Compare,
  # NB: Do not add ast.Not: the "not" operator cannot be overridden and must be
  # be converted to ~.
  ast.UnaryOp,
)


_COMMENT_REGEX = re.compile(r'^(\s*)(#.*)$')


_DIMENSION_DEFINITION_OPERATORS = (
  ast.LtE,
  ast.In,
  ast.Is,
)


_CrossProductDimension = collections.namedtuple(
    '_CrossProductDimension', ['targets', 'args'])
_SingleDimension = collections.namedtuple(
    '_SingleDimension', ['targets', 'args'])
_VariableDimension = collections.namedtuple(
    '_VariableDimension', ['targets', 'args'])


_LOAD = ast.Load()
_STORE = ast.Store()


def transform(program):
  cleaned = textwrap.dedent(program.strip('\n'))
  lines = cleaned.split('\n')
  for i, line in enumerate(lines):
    match = _COMMENT_REGEX.match(line)
    if match and match.groups():
      lines[i] = '%s%s' % (match.groups()[0], repr(match.groups()[1]))
  visited = _GrammarTransformer().visit(ast.parse('\n'.join(lines)))
  ast.fix_missing_locations(visited)
  return visited


class _GrammarTransformer(ast.NodeTransformer):
  def __init__(self):
    super(_GrammarTransformer, self).__init__()
    self._references = {}
    self._auto_constrain = True

  def _constrain_expr(self, expr):
    if self._auto_constrain:
      return _constrain_expr(expr)
    return expr

  def _register_reference(self, reference):
    if reference == '_':
      return
    name = _dimension_name(reference, ctx=_LOAD)
    self._references[name.id] = name

  def _find_and_register_references(self, targets):
    for target in targets:
      if isinstance(target, ast.Tuple):
        self._find_and_register_references(target.elts)
      elif isinstance(target, ast.Name):
        self._register_reference(target.id)

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
      result = _mutual_equality_expression(node)
      if result != node:
        return self.visit(result)
      return self.generic_visit(node)
    elif isinstance(dimensions, (_SingleDimension, _CrossProductDimension)):
      targets, args = dimensions
      self._find_and_register_references(targets)
      return ast.Assign(
          targets=targets,
          value=ast.Call(
              func=ast.Name(id='dimensions', ctx=_LOAD),
              args=args,
              keywords=[],
          )
      )
    elif isinstance(dimensions, _VariableDimension):
      targets, args = dimensions
      self._find_and_register_references(targets)
      return ast.Assign(
          targets=targets,
          value=ast.Call(
              func=ast.Name(id='variable', ctx=_LOAD),
              args=args,
              keywords=[],
          )
      )
    _fail(node, msg='Unable to transform dimension definition')

  def visit_For(self, node):
    node.target = self.visit(node.target)
    node.iter = self.visit(node.iter)
    body = []
    for expr in node.body:
      body.append(self._constrain_expr(self.visit(expr)))
    node.body = body
    orelse = []
    for expr in node.orelse:
      orelse.append(self._constrain_expr(self.visit(expr)))
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
    if not self._auto_constrain:
      return self.generic_visit(node)
    if len(node.body) == 0:
      _fail(node, msg='If statement missing body expressions')
    test = self.visit(node.test)
    body = self.visit_if_body(node.body)
    orelse = self.visit_if_body(node.orelse)
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
      result.append(self._constrain_expr(self.visit(constraint)))
    return ast.If(
        test=ast.Str(s=astor.to_source(node.test).replace('\n', ' ').strip()),
        body=result,
        orelse=[],
    )

  def visit_if_body(self, nodes):
    result = []
    for child in nodes:
      if isinstance(child, ast.If):
        constraints, body, orelse = _collect_conditional_constraints(
            child.test,
            self.visit_if_body(child.body),
            self.visit_if_body(child.orelse))
        if body or orelse:
          remaining = ast.If(
              test=child.test, body=child.body, orelse=child.orelse)
          _fail(remaining, msg='inner if statement expressions unconverted')
        for constraint in constraints:
          result.append(self.visit(constraint))
      else:
        result.append(child)
    return result

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
          body.append(self._constrain_expr(ast.Expr(value=child)))
      else:
        body.append(self._constrain_expr(result))
    node.body = body
    return node

  def visit_Str(self, node):
    canonical_reference_name = _canonical_reference_name(node.s)
    if canonical_reference_name in self._references:
      return self._references[canonical_reference_name]
    return self.generic_visit(node)

  def visit_UnaryOp(self, node):
    # Rewrite "not" to "~" so that operator overloading works.
    if isinstance(node.op, ast.Not):
      node.op = ast.Invert()
    return self.generic_visit(node)

  def visit_With(self, node):
    original_value = self._auto_constrain
    self._auto_constrain = False
    result = self.generic_visit(node)
    self._auto_constrain = original_value
    return result


def _fail(node, msg='Visit error'):
  try:
    raise NotImplementedError('%s (in ast.%s). Source:\n\t\t\t%s' % (
      msg, node.__class__.__name__, astor.to_source(node)))
  except AttributeError:  # Astor was unable to convert the source.
    raise NotImplementedError('%s (in ast.%s).' % (
      msg, node.__class__.__name__))


def _canonical_reference_name(value):
  if (isinstance(value, int) or
      (isinstance(value, str) and value and value[0].isdigit())):
    value = '_%s' % value
  elif isinstance(value, str):
    pass
  else:
    raise TypeError('Value "%s" is not a valid reference' % value)
  return value.replace(' ', '_').replace('-', '_').lower()


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
      len(node.ops) == 1 and
      isinstance(node.ops[0], _DIMENSION_DEFINITION_OPERATORS) and
      len(node.comparators) == 1
  )
  if not compare_match:
    return None
  if isinstance(node.ops[0], ast.Is):
    return _variable_definition(node)
  if isinstance(node.left, ast.Name):
    return _single_dimension_definition(node)
  if isinstance(node.left, ast.Tuple):
    return _cross_product_dimension_definition(node)
  return None


def _variable_definition(node):
  dimension = node.left
  targets = [_dimension_name(dimension.id, _STORE)]
  args = []
  comparator = node.comparators[0]
  if isinstance(comparator, ast.Name) and comparator.id == 'bool':
    pass  # "bool" is the default Variable type.
  elif (
      isinstance(comparator, ast.Call) and
      isinstance(comparator.func, ast.Name) and
      comparator.func.id == 'range'):
    args.extend(comparator.args)
  # Name always last argument.
  args.append(_ast_factory.coerce_value(dimension.id))
  return _VariableDimension(targets, args)


def _single_dimension_definition(node):
  comparator = node.comparators[0]
  if (isinstance(comparator, ast.BinOp) and
      isinstance(comparator.op, ast.Mult) and
      isinstance(comparator.left, ast.Num)):
    count = comparator.left
    comparator = comparator.right
  else:
    count = None
  values = _dimension_values(comparator)
  if values:
    dimension = node.left.id
    targets = []
    if not isinstance(values, ast.AST):
      targets.append(
        ast.Tuple(
          elts=[_dimension_name(value, _STORE) for value in values],
          ctx=_STORE,
        ),
      )
    targets.append(_dimension_name(dimension, _STORE))
    args = [dimension]
    if count is not None:
      args.append(count)
    args.append(values)
    return _SingleDimension(
        targets, [_ast_factory.coerce_value(args)])
  return None


def _cross_product_dimension_definition(node):
  if (not isinstance(node.left, ast.Tuple) or
      len(node.comparators) != 1 or
      not isinstance(node.comparators[0], ast.Tuple) or
      len(node.left.elts) != len(node.comparators[0].elts) or
      not all(isinstance(n, ast.Name) for n in node.left.elts) or
      not all(isinstance(n, ast.Set) for n in node.comparators[0].elts)):
    _fail(node, 'Invalid cross-product dimension definition')
  targets = []
  dimension_names = [n.id for n in node.left.elts]
  dimension_values = [_dimension_values(n) for n in node.comparators[0].elts]
  # Goal: (x1, x2, x3, y1, y2, y3), _, ... = a, b, ... = a_b_...
  # 1: (x1, x2, x3, y1, y2, y3), _, ...
  # 1a: ^---^---^---^---^---^...
  elts = []
  for parts in itertools.product(*dimension_values):
    elts.append(_dimension_name(''.join(map(str, parts)), _STORE))
  # 1: (x1, x2, x3, y1, y2, y3), _, ...
  # 1b: ^------------------------^--^...
  group_elts = [
    ast.Tuple(
        elts=elts,
        ctx=_STORE,
    )
  ] + [ast.Name(id='_', ctx=_STORE)] * (len(dimension_names) - 1)
  targets.append(
      ast.Tuple(
          elts=group_elts,
          ctx=_STORE,
      )
  )
  # 2: a, b, ...
  targets.append(ast.Tuple(
      elts=[_dimension_name(name, _STORE) for name in dimension_names],
      ctx=_STORE,
  ))
  # 3: a_b_...
  targets.append(_dimension_name('_'.join(dimension_names), _STORE))
  # Goal args: [('a', ['x', 'y']), ('b', [1, 2, 3]), ...
  dimension_args = zip(dimension_names, dimension_values)
  args = [_ast_factory.coerce_value(arg) for arg in dimension_args]
  return _CrossProductDimension(targets, args)


def _dimension_values(node):
  if isinstance(node, ast.Set):
    values = []
    for value in node.elts:
      if isinstance(value, _REFERENCE_TYPES):
        values.append(value)
      elif (isinstance(value, ast.BinOp) and
          isinstance(value.op, ast.Mult) and
          isinstance(value.left, _REFERENCE_TYPES) and
          isinstance(value.right, ast.Num)):
        for i in range(value.right.n):
          values.append(value.left)
      else:
        _fail(value, msg='Unable to parse dimension definition value')
    if not all(isinstance(value, _REFERENCE_TYPES) for value in values):
      return None
    return [_dimension_name_value(value) for value in values]
  elif isinstance(node, ast.Call):
    return node
  return None


def _dimension_name_value(node):
  if isinstance(node, ast.Name):
    result = node.id
  else:
    result = _util.literal_value(node)
  if not isinstance(result, (str, int)):
    _fail(node, msg='Unable to identify dimension node name')
  return result


def _dimension_target_tuple(values):
  return ast.Tuple(
      elts=[_dimension_name(value, _STORE) for value in values],
      ctx=_STORE,
  )


def _dimension_name(dimension, ctx):
  return ast.Name(id=_canonical_reference_name(dimension), ctx=ctx)


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
        targets=[ast.Name(id=key, ctx=_STORE)],
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


def _mutual_equality_expression(node):
  result = _mutual_equality_expression_value(node.value)
  return result or node


def _mutual_equality_expression_value(node):
  if not (isinstance(node, ast.Compare) and
    isinstance(node.left, ast.Set) and len(node.ops) == 1 and
    isinstance(node.comparators[0], ast.Set)):
    return None
  if isinstance(node.ops[0], ast.Eq):
    equal = True
  elif isinstance(node.ops[0], ast.NotEq):
    equal = False
  else:
    raise _fail(node, msg='Unsupported equality expression')
  return _mutual_equality_for(node.left, node.comparators[0], equal)

def _mutual_equality_for(a, b, equal):
  if len(a.elts) > len(b.elts):
    a, b = b, a
  if equal:
    op = ast.Eq()
  else:
    op = ast.NotEq()
  return ast.For(
      target=ast.Name(id='__x', ctx=_STORE),
      iter=a,
      body=[
        ast.Expr(value=ast.Compare(
            left=ast.Call(
                func=ast.Name(id='sum', ctx=_LOAD),
                args=[
                  ast.GeneratorExp(
                      elt=ast.Subscript(
                          value=ast.Name(id='__x', ctx=_LOAD),
                          slice=ast.Index(
                              value=ast.Name(id='__y', ctx=_LOAD),
                          ),
                          ctx=_LOAD,
                      ),
                      generators=[
                        ast.comprehension(
                            target=ast.Name(id='__y', ctx=_STORE),
                            iter=b,
                            ifs=[],
                            is_async=0,
                        ),
                      ],
                  ),
                ],
                keywords=[],
            ),
            ops=[op],
            comparators=[ast.Num(n=1)],
        )),
      ],
      orelse=[],
  )

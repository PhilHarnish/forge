import ast
import re
import textwrap

import astor

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

  def _dimension_definitions(self, node):
    if (not isinstance(node, ast.Compare) or
        not isinstance(node.left, ast.Name) or
        len(node.ops) != 1 or
        not isinstance(node.ops[0], ast.LtE) or
        len(node.comparators) != 1 or
        not isinstance(node.comparators[0], ast.Set)):
      return None
    values = node.comparators[0].elts
    if not all(isinstance(value, _REFERENCE_TYPES) for value in values):
      return None
    dimension = node.left.id
    return {
      dimension: [_dimension_name(value) for value in values]
    }

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

  def visit_Expr(self, node):
    # This may be a dimensions definition.
    value = node.value
    dimensions = self._dimension_definitions(value)
    if not dimensions:
      return self.generic_visit(node)
    elif len(dimensions) == 1:
      dimension, values = next(iter(dimensions.items()))
      self._register_references(dimension, *values)
      node = ast.Assign(
          targets=[
            _dimension_target_tuple(values),
            _dimension_target_dimension(dimension),
          ],
          value=_dimension_value(dimension, values),
      )
      return node
    _fail(node)

  def visit_If(self, node):
    """Converts "if A: B" to "A <= B"."""
    condition = self.visit(node.test)
    implication = self.visit(_combine_expressions(node.body))
    result = ast.Compare(
        left=condition,
        ops=[ast.LtE()],
        comparators=[implication],
    )
    if node.orelse:
      # Convert "else: C" into "A + C >= 1".
      implication = self.visit(_combine_expressions(node.orelse))
      else_result = ast.Compare(
          left=ast.BinOp(
              left=condition,
              op=ast.Add(),
              right=implication,
          ),
          ops=[ast.GtE()],
          comparators=[ast.Num(n=1)],
      )
      result = ast.BinOp(
          left=result,
          op=ast.BitAnd(),
          right=else_result,
      )
    return ast.Expr(value=result)

  def visit_Name(self, node):
    canonical_reference_name = _canonical_reference_name(node.id)
    if canonical_reference_name in self._references:
      return self._references[canonical_reference_name]
    return self.generic_visit(node)

  def visit_Module(self, node):
    body = _HEADER.copy()
    for expr in node.body:
      expr = self.visit(expr)
      if isinstance(expr, ast.Expr):
        expr.value = _constrain_comparison(expr.value)
      body.append(expr)
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
  dimensions = []
  for value in values:
    if isinstance(value, str):
      dimensions.append(ast.Str(s=value))
    else:
      dimensions.append(ast.Num(n=value))
  return ast.Call(
      func=ast.Name(
          id='dimensions',
          ctx=ast.Load(),
      ),
      args=[],
      keywords=[
        ast.keyword(
            arg=dimension,
            value=ast.List(
                elts=dimensions,
                ctx=ast.Load(),
            )
        )
      ],
  )


def _combine_expressions(exprs):
  if (not all(isinstance(expr, ast.Expr) for expr in exprs)):
    _fail(ast.Module(body=exprs), 'Unable to combine expressions')
  if len(exprs) > 1:
    # Multiple expressions should be AND'd.
    return ast.BoolOp(
        op=ast.And(),
        values=[
          expr.value for expr in exprs
        ]
    )
  return exprs[0].value

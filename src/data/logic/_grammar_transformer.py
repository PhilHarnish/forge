import ast

import astor

_HEADER = ast.parse("""
from data.logic.dsl import *
dimensions = DimensionFactory()
model = Model(dimensions)
""").body


_REFERENCE_TYPES = (
  ast.Name,
  ast.Str,
  ast.Num,
)


class _GrammarTransformer(ast.NodeTransformer):
  def __init__(self, src):
    super(_GrammarTransformer, self).__init__()
    self._src = src.split('\n')
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

  def visit_Compare(self, node):
    # This may be a dimensions definition.
    dimensions = self._dimension_definitions(node)
    if not dimensions:
      return self.generic_visit(node)
    elif len(dimensions) == 1:
      dimension, values = next(iter(dimensions.items()))
      node = ast.Assign(
          targets=[
            _dimension_target_tuple(values),
            _dimension_target_dimension(dimension),
          ],
          value=_dimension_value(dimension, values),
      )
      return node
    _fail(node)

  def visit_Module(self, node):
    node.body = _HEADER + node.body
    return self.generic_visit(node)

  def _msg(self, node, msg):
    return '\n'.join([
      msg,
      self._src[node.lineno],
      '-' * node.col_offset + '^',
    ])


def _fail(node, msg='Visit error'):
  try:
    raise NotImplementedError('%s (in ast.%s). Source:\n\t\t\t%s' % (
      msg, node.__class__.__name__, astor.to_source(node)))
  except AttributeError:  # Astor was unable to convert the source.
    raise NotImplementedError('%s (in ast.%s).' % (
      msg, node.__class__.__name__))


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
    if isinstance(value, str):
      name = value.replace(' ', '_')
    else:
      name = '_%s' % value
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
  dimensions = [ast.Str(s=value) for value in values]
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

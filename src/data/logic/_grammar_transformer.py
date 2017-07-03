import ast


_HEADER = ast.parse("""
from data.logic.dsl import *
dimensions = DimensionFactory()
model = Model(dimensions)
""").body


class _GrammarTransformer(ast.NodeTransformer):
  def __init__(self, src):
    super(_GrammarTransformer, self).__init__()
    self._src = src.split('\n')

  def visit_Module(self, node):
    node.body = _HEADER + node.body
    return self.generic_visit(node)

  def _msg(self, node, msg):
    return '\n'.join([
      msg,
      self._src[node.lineno],
      '-' * node.col_offset + '^',
    ])

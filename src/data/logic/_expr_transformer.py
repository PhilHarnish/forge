import ast

import Numberjack
import astor


class ExprTransformer(ast.NodeTransformer):
  """Visits and replaces an AST with Numberjack primitives.

  Very strict about support. Unexpected AST nodes will raise.
  """

  def __init__(self, model):
    self._model = model

  def compile(self, node):
    if not isinstance(node, ast.Expr):
      raise TypeError('%s cannot be compiled' % node)
    result = self.visit(node)
    if isinstance(result, ast.AST):
      raise _fail(node)
    return result

  def visit(self, node):
    result = super(ExprTransformer, self).visit(node)
    if isinstance(result, ast.AST):
      # The entire tree must be converted.
      _fail(node)
    return result

  def generic_visit(self, node):
    # All visited nodes must be supported.
    _fail(node)

  def visit_Compare(self, node):
    left = self.visit(node.left)
    comparators = [self.visit(comparator) for comparator in node.comparators]
    for op, right in zip(node.ops, comparators):
      if isinstance(op, ast.Eq):
        left = (left == right)
      elif isinstance(op, ast.NotEq):
        left = (left != right)
      else:
        _fail(node, msg='Comparing %s unsupported' % op.__class__.__name__)
    return left

  def visit_Expr(self, node):
    result = self.visit(node.value)  # Expr is a wrapper on `value`.
    if isinstance(result, Numberjack.Predicate):
      return result
    # Every expression is implicitly true.
    return result == True

  def visit_Name(self, node):
    if not isinstance(node.ctx, ast.Load):
      raise TypeError('ast.Name only supports ast.Load')
    return self._model.resolve(node.id)


def _fail(node, msg='Visit error'):
  try:
    raise NotImplementedError('%s (in ast.%s). Source:\n\t\t\t%s' % (
      msg, node.__class__.__name__, astor.to_source(node)))
  except AttributeError:  # Astor was unable to convert the source.
    raise NotImplementedError('%s (in ast.%s).' % (
      msg, node.__class__.__name__))

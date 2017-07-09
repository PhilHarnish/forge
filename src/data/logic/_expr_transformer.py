import ast

import Numberjack
import astor

from data.logic import _predicates


class ExprTransformer(ast.NodeTransformer):
  """Visits and replaces an AST with Numberjack primitives.

  Very strict about support. Unexpected AST nodes will raise.
  """

  def __init__(self, model):
    self._model = model

  def compile(self, node):
    result = self.visit(node)
    if not isinstance(result, (Numberjack.Predicate, _predicates.Predicates)):
      _fail(node, msg='Failed to compile. %s (%s) remains' % (
          type(result), result))
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

  def visit__DimensionSlice(self, slice):
    # This can happen when a slice is being used without any comparisons.
    # We can assume this slice is intended to be true.
    return self.visit(slice == True)

  def visit_BinOp(self, node):
    left = self.visit(node.left)
    right = self.visit(node.right)
    op = node.op
    if isinstance(op, ast.BitAnd):
      return left & right
    elif isinstance(op, ast.BitOr):
      return left | right
    elif isinstance(op, ast.BitXor):
      # This shortcut may not always work. When does it fail?
      return left + right == 1
    elif isinstance(op, ast.Add):
      return left + right
    elif isinstance(op, ast.Sub):
      return left - right
    elif isinstance(op, ast.Mult):
      return left * right
    _fail(node, msg='Binary op %s unsupported' % op.__class__.__name__)

  def visit_Call(self, node):
    if not isinstance(node.func, ast.Name):
      _fail(node.func, msg='func is %s, not ast.Name' % type(node.func))
    fn = node.func.id
    if not hasattr(Numberjack, fn) or not callable(getattr(Numberjack, fn)):
      _fail(node.func, msg='Unable to resolve fn %s on Numberjack' % fn)
    args = [self.visit(arg) for arg in node.args]
    # Wrap result in a Predicates object so that our operator overloading takes
    # precedence.
    return _predicates.Predicates([getattr(Numberjack, fn)(*args)])

  def visit_Compare(self, node):
    left = self.visit(node.left)
    comparators = [self.visit(comparator) for comparator in node.comparators]
    for op, right in zip(node.ops, comparators):
      if isinstance(op, ast.Eq):
        left = (left == right)
      elif isinstance(op, ast.NotEq):
        left = (left != right)
      elif isinstance(op, ast.Gt):
        left = (left > right)
      elif isinstance(op, ast.GtE):
        left = (left >= right)
      elif isinstance(op, ast.Lt):
        left = (left < right)
      elif isinstance(op, ast.LtE):
        left = (left <= right)
      else:
        _fail(node, msg='Comparing %s unsupported' % op.__class__.__name__)
    return left

  def visit_Expr(self, node):
    result = self.visit(node.value)  # Expr is a wrapper on `value`.
    if isinstance(result, (_predicates.Predicates, Numberjack.Predicate)):
      return result
    # Every expression is implicitly true.
    return result == True

  def visit_List(self, node):
    return [self.visit(i) for i in node.elts]

  def visit_Name(self, node):
    if not isinstance(node.ctx, ast.Load):
      raise TypeError('ast.Name only supports ast.Load')
    return self._model.resolve(node.id)

  def visit_NameConstant(self, node):
    return node.value

  def visit_Num(self, node):
    return self._model.resolve_value(node.n)

  def visit_Str(self, node):
    return self._model.resolve_value(node.s)


def _fail(node, msg='Visit error'):
  try:
    raise NotImplementedError('%s (in ast.%s). Source:\n\t\t\t%s' % (
      msg, node.__class__.__name__, astor.to_source(node)))
  except:  # Astor was unable to convert the source.
    raise NotImplementedError('%s (in ast.%s).' % (
        msg, node.__class__.__name__))

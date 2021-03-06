import ast
import builtins
import types

import Numberjack
import astor

from data.logic import _predicates

_EXPECTED_COMPILE_OUTPUT = (
  types.FunctionType,
  Numberjack.Predicate,
  _predicates.Predicates,
)


class ExprTransformer(ast.NodeTransformer):
  """Visits and replaces an AST with Numberjack primitives.

  Very strict about support. Unexpected AST nodes will raise.
  """

  def __init__(self, model):
    self._model = model

  def compile(self, node):
    result = self.visit(node)
    if not isinstance(result, _EXPECTED_COMPILE_OUTPUT):
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
      result = left & right
    elif isinstance(op, ast.BitOr):
      result = left | right
    elif isinstance(op, ast.BitXor):
      # This shortcut may not always work. When does it fail?
      result = left + right == 1
    elif isinstance(op, ast.Add):
      result = left + right
    elif isinstance(op, ast.Sub):
      result = left - right
    elif isinstance(op, ast.Mult):
      result = left * right
    elif isinstance(op, ast.LShift):
      result = left << right
    elif isinstance(op, ast.RShift):
      result = left >> right
    else:
      raise _fail(node, msg='Binary op %s unsupported' % op.__class__.__name__)
    return _predicates.Predicates([result])

  def visit_Call(self, node):
    args = [self.visit(arg) for arg in node.args]
    kwargs = {}  # TODO: Support kwargs.
    if isinstance(node.func, ast.Name):
      fn = getattr(builtins, node.func.id)
    elif callable(node.func):  # Normally illegal. See _sugar.py.
      fn = node.func
    else:
      raise _fail(node, msg='Unsupported ast.Call function')
    # Wrap result in a Predicates object so that our operator overloading takes
    # precedence.
    return _predicates.Predicates([fn(*args, **kwargs)])

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
    # Unary inputs and predicate outputs require bool coercion.
    requires_coercion = isinstance(node.value, ast.UnaryOp) or not isinstance(
        result, (_predicates.Predicates, Numberjack.Predicate))
    if requires_coercion:
      # Every expression is implicitly true. Attempt to coerce it to a boolean.
      return result == True
    # No extra work required for most other expressions.
    return result

  def visit_List(self, node):
    # We assume list values will not participate in more accumulating
    # expressions. Coerce them to their final values.
    return [self._model.coerce_value(self.visit(i)) for i in node.elts]

  def visit_Name(self, node):
    if not isinstance(node.ctx, ast.Load):
      raise TypeError('ast.Name only supports ast.Load')
    return self._model.resolve(node.id)

  def visit_NameConstant(self, node):
    return self._model.resolve_value(node.value)

  def visit_Num(self, node):
    return self._model.resolve_value(node.n)

  def visit_Str(self, node):
    return self._model.resolve_value(node.s)

  def visit_UnaryOp(self, node):
    op = node.op
    result = self.visit(node.operand)
    if isinstance(op, ast.Invert):
      return 1 - result
    _fail(node, msg='Unary operator %s unsupported' % op.__class__.__name__)


def _fail(node, msg='Visit error'):
  try:
    raise NotImplementedError('%s (in %s). Source:\n\t\t\t%s' % (
      msg, node.__class__, astor.to_source(node)))
  except:  # Astor was unable to convert the source.
    raise NotImplementedError('%s (in %s).' % (msg, node.__class__))

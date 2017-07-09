import ast

from data.logic import _addressable_value

_OPERATOR_MAP = {
  '+': ast.Add,
  '&': ast.BitAnd,
  '==': ast.Eq,
  '!=': ast.NotEq,
  '|': ast.BitOr,
  '^': ast.BitXor,
  '-': ast.Sub,
  '>': ast.Gt,
  '>=': ast.GtE,
  '<': ast.Lt,
  '<=': ast.LtE,
  '*': ast.Mult,
}


class AccumulatingExpressionMixin(object):
  def __and__(self, other):
    return bin_op(self, '&', other)

  def __rand__(self, other):
    return bin_op(other, '&', self)

  def __add__(self, other):
    return bin_op(self, '+', other)

  def __radd__(self, other):
    return bin_op(other, '+', self)

  def __eq__(self, other):
    return compare(self, ['=='], [other])

  def __gt__(self, other):
    return compare(self, ['>'], [other])

  def __ge__(self, other):
    return compare(self, ['>='], [other])

  def __lt__(self, other):
    return compare(self, ['<'], [other])

  def __le__(self, other):
    return compare(self, ['<='], [other])

  def __sub__(self, other):
    return bin_op(self, '-', other)

  def __rsub__(self, other):
    return bin_op(other, '-', self)

  def __ne__(self, other):
    return compare(self, ['!='], [other])

  def __mul__(self, other):
    return bin_op(self, '*', other)

  def __rmul__(self, other):
    return bin_op(other, '*', self)

  def __or__(self, other):
    return bin_op(self, '|', other)

  def __xor__(self, other):
    return bin_op(self, '^', other)


class AccumulatingExpr(ast.Expr, AccumulatingExpressionMixin):
  """Overloads operators and accumulate expressions at runtime."""


# Cloak as an "Expr" object to blend in with AST libraries.
AccumulatingExpr.__name__ = 'Expr'


def bin_op(left, op, right):
  return AccumulatingExpr(
      value=ast.BinOp(
          left=coerce_value(left),
          op=coerce_operator(op),
          right=coerce_value(right),
      )
  )


def compare(left, ops, comparators):
  assert len(ops) > 0, '1+ comparisons required'
  assert len(ops) == len(comparators), 'unable to compare %s, %s using %s' % (
    left, comparators, ops)
  return AccumulatingExpr(
      value=ast.Compare(
          left=coerce_value(left),
          ops=[coerce_operator(op) for op in ops],
          comparators=[coerce_value(comparator) for comparator in comparators]
      )
  )


def coerce_operator(op):
  return _OPERATOR_MAP[op]()


def coerce_value(value):
  if isinstance(value, ast.Expr):
    return value.value  # Prevent excessive nesting.
  elif isinstance(value, ast.AST):
    return value
  elif isinstance(value, bool):
    return ast.NameConstant(value=value)
  elif isinstance(value, (int, float)):
    return ast.Num(n=value)
  elif isinstance(value, str):
    return ast.Str(s=value)
  elif isinstance(value, _addressable_value.AddressableValue):
    return ast.Name(id=value.dimension_address(), ctx=ast.Load())
  raise TypeError('unable to coerce %s' % value)

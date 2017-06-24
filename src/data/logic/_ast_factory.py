import ast

from data.logic import _addressable_value

_OPERATOR_MAP = {
  '+': ast.Add,
  '==': ast.Eq,
  '!=': ast.NotEq,
  '-': ast.Sub,
}


class AccumulatingExpressionMixin(object):
  def __add__(self, other):
    return bin_op(self, '+', other)

  def __eq__(self, other):
    return compare(self, ['=='], [other])

  def __sub__(self, other):
    return bin_op(self, '-', other)

  def __ne__(self, other):
    return compare(self, ['!='], [other])


class AccumulatingExpr(ast.Expr, AccumulatingExpressionMixin):
  """Overloads operators and accumulate expressions at runtime."""


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
  if isinstance(value, bool):
    return ast.NameConstant(value=value)
  elif isinstance(value, (int, float)):
    return ast.Num(n=value)
  elif isinstance(value, str):
    return ast.Str(s=value)
  elif isinstance(value, _addressable_value.AddressableValue):
    return ast.Name(id=value.dimension_address_name(), ctx=ast.Load())
  raise TypeError('unable to coerce %s' % value)

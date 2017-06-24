import ast

from data.logic import _addressable_value

_OPERATOR_MAP = {
  '==': ast.Eq,
}


class AccumulatingExpressionMixin(object):
  def __eq__(self, other):
    return compare(self, ['=='], [other])


class AccumulatingExpr(ast.Expr, AccumulatingExpressionMixin):
  """Overloads operators and accumulate expressions at runtime."""


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

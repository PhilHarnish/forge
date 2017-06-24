import ast

from data.logic import _dimension_slice

_OPERATOR_MAP = {
  '==': ast.Eq,
}


def compare(left, ops, comparators):
  assert len(ops) > 0, '1+ comparisons required'
  assert len(ops) == len(comparators), 'unable to compare %s, %s using %s' % (
    left, comparators, ops)
  return ast.Compare(
      left=left,
      ops=[coerce_operator(op) for op in ops],
      comparators=[coerce_value(comparator) for comparator in comparators])


def coerce_operator(op):
  return _OPERATOR_MAP[op]()


def coerce_value(value):
  if isinstance(value, bool):
    return ast.NameConstant(value=value)
  elif isinstance(value, (int, float)):
    return ast.Num(n=value)
  elif isinstance(value, str):
    return ast.Str(s=value)
  elif isinstance(value, _dimension_slice._DimensionSlice):
    return ast.Name(id=value.dimension_address_name(), ctx=ast.Load())
  raise TypeError('unable to coerce %s' % value)

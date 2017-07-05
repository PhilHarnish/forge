# Maps binary operators to their swapped complement.
import operator

_OPERATORS = {
  # Comparators.
  '__eq__': '__eq__',
  '__ne__': '__ne__',
  '__lt__': '__gt__',
  '__le__': '__ge__',
  # Binary operators.
  '__add__': '__radd__',
  '__sub__': '__rsub__',
  '__or__': '__ror__',
  '__xor__': '__rxor__',
}


def _reversed_operator(op):
  def reversed(left, right):
    return op(right, left)

  return reversed


def overload_with_fn(fn):
  def wrapper(cls):
    for op, rop in _OPERATORS.items():
      op_fn = getattr(operator, op)
      if hasattr(operator, rop):
        rop_fn = getattr(operator, rop)
      else:
        rop_fn = _reversed_operator(op_fn)
      setattr(cls, op, fn(op_fn, rop_fn))
      if op != rop:
        setattr(cls, rop, fn(rop_fn, op_fn))
    return cls
  return wrapper


class OverloadedSelfBase(object):
  def __eq__(self, other):
    return self

  def __ne__(self, other):
    return self

  def __lt__(self, other):
    return self

  def __gt__(self, other):
    return self

  def __le__(self, other):
    return self

  def __ge__(self, other):
    return self

  def __add__(self, other):
    return self

  def __radd__(self, other):
    return self
  def __sub__(self, other):
    return self

  def __rsub__(self, other):
    return self

  def __or__(self, other):
    return self

  def __ror__(self, other):
    return self

  def __xor__(self, other):
    return self

  def __rxor__(self, other):
    return self
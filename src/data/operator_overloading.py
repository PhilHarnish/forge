# Maps binary operators to their swapped complement.
import operator

_OPERATORS = {
  # Comparators.
  '__eq__': '__eq__',
  '__ne__': '__ne__',
  '__lt__': '__gt__',
  '__le__': '__ge__',
  # Binary operators.
  '__and__': '__rand__',
  '__add__': '__radd__',
  '__mul__': '__rmul__',
  '__sub__': '__rsub__',
  '__or__': '__ror__',
  '__xor__': '__rxor__',
}


def _reversed_operator(name, op):
  def reversed(left, right):
    # If possible, explicitly call left.__rop__(right).
    # The native rop(right, left) can silently un-reverse arguments.
    if hasattr(left, name):
      # We must implement the "NotImplented" semantics ourselves.
      try:
        result = getattr(left, name)(right)
        if result is not NotImplemented:
          return result
      except NotImplementedError:
        pass
    return op(right, left)

  return reversed


def overload_with_fn(fn):
  def wrapper(cls):
    for op, rop in _OPERATORS.items():
      op_fn = getattr(operator, op)
      if hasattr(operator, rop):
        rop_fn = getattr(operator, rop)
      else:
        rop_fn = _reversed_operator(rop, op_fn)
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

  def __mul__(self, other):
    return self

  def __rmul__(self, other):
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

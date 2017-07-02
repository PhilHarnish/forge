import operator

import Numberjack

# Try to de-prioritize any Numberjack primitives so that our operators
# take precedence.
_LOWER_PRIORITY = (
  Numberjack.Predicate,
)

# Maps binary operators to their swapped complement.
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


class Predicates(list):
  def __str__(self):
    return '\n'.join(map(str, self))


def _make_operator(op, rop):
  def fn(self, other):
    children = []
    for child in self:
      if isinstance(child, _LOWER_PRIORITY):
        children.append(rop(other, child))
      else:
        children.append(op(child, other))
    return Predicates(children)

  return fn


def _reversed_operator(op):
  def reversed(left, right):
    return op(right, left)

  return reversed


for op, rop in _OPERATORS.items():
  op_fn = getattr(operator, op)
  if hasattr(operator, rop):
    rop_fn = getattr(operator, rop)
  else:
    rop_fn = _reversed_operator(op_fn)
  setattr(Predicates, op, _make_operator(op_fn, rop_fn))
  if op != rop:
    setattr(Predicates, rop, _make_operator(rop_fn, op_fn))

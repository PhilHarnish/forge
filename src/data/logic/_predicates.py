import Numberjack

# Try to de-prioritize any Numberjack primitives so that our operators
# take precedence.
from data import operator_overloading

_LOWER_PRIORITY = (
  Numberjack.Predicate,
)


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


@operator_overloading.overload_with_fn(_make_operator)
class Predicates(list):
  def __str__(self):
    return '\n'.join(map(str, self))

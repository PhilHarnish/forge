import Numberjack

from data import operator_overloading
from data.logic import _util

# Try to de-prioritize any Numberjack primitives so that our operators
# take precedence.
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
  def __init__(self, children):
    if len(children) == 1 and isinstance(children[0], list):
      # Try to prevent needless nesting.
      children = children[0]
    super(Predicates, self).__init__(children)

  def __str__(self):
    result = []
    for value in self:
      if isinstance(value, Numberjack.Expression):
        try:
          solution = _util.numberjack_solution(value)
          result.append('%s == %s' % (solution, value))
        except ValueError:
          result.append(str(value))
      else:
        result.append(str(value))
    return '\n'.join(result)

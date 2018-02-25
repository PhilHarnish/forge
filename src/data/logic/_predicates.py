from typing import Any, Callable

import Numberjack

from data import operator_overloading
from data.logic import _util

# Try to de-prioritize any Numberjack primitives so that our operators
# take precedence.
_LOWER_PRIORITY = (
  Numberjack.Predicate,
)
_BinOp = Callable[[Any, Any], Any]

def _make_operator(
    op: _BinOp, rop: _BinOp) -> Callable[['Predicates', Any], 'Predicates']:
  def fn(self: 'Predicates', other: Any):
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
  def __init__(self, children: list) -> None:
    if len(children) == 1 and isinstance(children[0], list):
      # Try to prevent needless nesting.
      children = children[0]
    super(Predicates, self).__init__(children)

  def __str__(self) -> str:
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

  def value(self) -> int:
    assert len(self) == 1, 'Only able to evaluate predicate with one expression'
    try:
      return _util.numberjack_solution(self[0])
    except ValueError as e:
      if str(e).endswith('is not built'):
        return 0
      raise

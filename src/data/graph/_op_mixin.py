import itertools
from typing import Any, NewType, Optional, Union

from data import pool

OperatorType = NewType('OperatorType', int)


_next = itertools.count()
OP_IDENTITY = next(_next)
OP_ADD = next(_next)
OP_MULTIPLY = next(_next)
OP_DIV = next(_next)
OP_FLOOR_DIV = next(_next)
OP_CALL = next(_next)
_OPERATOR_STRINGS = [
  ('%s', ''),
  ('(%s)', '+'),
  ('(%s)', '*'),
  ('anagram(%s)', ', '),
  ('anagram(%s)', ', '),
  ('call(%s)', ', ')
]


class Op(object):
  __slots__ = ('_operator', '_operands')

  def __init__(self, operator: OperatorType, operands: list) -> None:
    self._operator = operator
    self._operands = operands

  def operator(self) -> int:
    return self._operator

  def operands(self) -> list:
    return self._operands

  def __eq__(self, other: Optional['Op']) -> bool:
    return other is not None and self._operator == other._operator

  def __len__(self) -> int:
    return len(self._operands)

  def __str__(self) -> str:
    fmt, mid = _OPERATOR_STRINGS[self._operator]
    return fmt % mid.join(map(repr, self._operands))

  __repr__ = __str__


IDENTITY = Op(OP_IDENTITY, [])


class OpMixin(pool.Pooled):
  __slots__ = ('op',)

  # Input operations for this node.
  op: Optional[Op]

  def __init__(self, op: Optional[Op] = None):
    super(OpMixin, self).__init__()
    self.op = op

  def __add__(self, other: Union[Any, 'OpMixin']) -> 'OpMixin':
    return _commutative(self, OP_ADD, other)

  def __call__(self, *args, **kwargs) -> 'OpMixin':
    return self.alloc(Op(OP_CALL, [self, args, kwargs]))

  def __mul__(self, other: Union[Any, 'OpMixin']) -> 'OpMixin':
    return _commutative(self, OP_MULTIPLY, other)

  def __truediv__(self, other: Union[Any, 'OpMixin']) -> 'OpMixin':
    return _noncommutative(self, OP_DIV, other)

  __rtruediv__ = __truediv__

  def __floordiv__(self, other: Union[Any, 'OpMixin']) -> 'OpMixin':
    return _noncommutative(self, OP_FLOOR_DIV, other)

  __rfloordiv__ = __floordiv__

  def __str__(self) -> str:
    return '%s(%s)' % (self.__class__.__name__, str(self.op or ''))

  __repr__ = __str__


def _commutative(
    source: OpMixin, operator: OperatorType, other: Any) -> OpMixin:
  children = []
  child = source.alloc(Op(operator, children))
  if child.op == source.op:
    children.extend(source.op.operands())
  else:
    children.append(source)
  if isinstance(other, OpMixin) and child.op == other.op:
    # Flatten repeated commutative operations.
    children.extend(other.op.operands())
  else:
    children.append(other)
  return child


def _noncommutative(
    source: OpMixin, operator: OperatorType, other: Any) -> OpMixin:
  children = []
  child = source.alloc(Op(operator, children))
  children.append(source)
  children.append(other)
  return child

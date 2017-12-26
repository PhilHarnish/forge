import itertools
from typing import Any, NewType, Optional, Union

from data import pool

OperatorType = NewType('OperatorType', int)


_next = itertools.count()
OP_IDENTITY = next(_next)
OP_ADD = next(_next)
OP_MULTIPLY = next(_next)
OP_AND = next(_next)
OP_OR = next(_next)
_OPERATOR_STRINGS = [
  ('%s', ''),
  ('(%s)', '+'),
  ('(%s)', '*'),
  ('(%s)', '&'),
  ('(%s)', '|'),
]


class Op(object):
  __slots__ = ('_operator', '_operands')

  def __init__(self, operator, operands) -> None:
    self._operator = operator
    self._operands = operands

  def operands(self) -> list:
    return self._operands

  def __eq__(self, other: 'Op') -> bool:
    return self._operator == other._operator

  def __str__(self) -> str:
    fmt, mid = _OPERATOR_STRINGS[self._operator]
    return fmt % mid.join(map(str, self._operands))

  __repr__ = __str__


IDENTITY = Op(OP_IDENTITY, [])


class OpMixin(pool.Pooled):
  __slots__ = ('op',)

  # Input operations for this node.
  op: Optional[Op]

  def __init__(self, op: Optional[Op] = None):
    super(OpMixin, self).__init__()
    if op is None:
      self.op = IDENTITY
    else:
      self.op = op

  def __add__(self, other: Union[int, float, 'OpMixin']) -> 'OpMixin':
    return _commutative(self, OP_ADD, other)

  def __mul__(self, other: Union[int, float, 'OpMixin']) -> 'OpMixin':
    return _commutative(self, OP_MULTIPLY, other)

  def __and__(self, other: Union[int, float, 'OpMixin']) -> 'OpMixin':
    return _commutative(self, OP_AND, other)

  def __or__(self, other: Union[int, float, 'OpMixin']) -> 'OpMixin':
    return _commutative(self, OP_OR, other)

  def __str__(self) -> str:
    return '%s(%s)' % (self.__class__.__name__, str(self.op))

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

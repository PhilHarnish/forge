import numbers
from typing import Any, Optional


class Validator(object):
  def __call__(self, *args, **kwargs) -> None:
    return None  # Fool runtime checks in typing module.

  def __instancecheck__(self, obj: Any) -> bool:
    raise NotImplementedError(
        'Validator %s missing __instancecheck__' % self.__class__.__name__)

  def __repr__(self) -> str:
    return '%s(%s)' % (self.__class__.__name__, self._args())

  def _args(self) -> str:
    return ''


class NumberInRange(Validator):
  _min_value: numbers.Number = float('-inf')
  _max_value: numbers.Number = float('inf')

  def __init__(
      self,
      min_value: Optional[numbers.Number] = None,
      max_value: Optional[numbers.Number] = None):
    if min_value is None and max_value is None:
      raise ValueError('min_value and max_value are both None')
    if min_value is not None:
      self._min_value = min_value
    if max_value is not None:
      self._max_value = max_value

  def __instancecheck__(self, obj: Any) -> bool:
    if not isinstance(obj, numbers.Number):
      return False
    return self._min_value <= obj <= self._max_value

  def _args(self) -> str:
    return 'min_value=%s, max_value=%s' % (self._min_value, self._max_value)

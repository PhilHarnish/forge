from typing import Any, Optional, TypeVar

Number = TypeVar('Number', int, float)


class Validator(object):
  def __call__(self, *args, **kwargs) -> None:
    return None  # Fool runtime checks in typing module.

  def __instancecheck__(self, obj: Any) -> bool:
    raise NotImplementedError(
        'Validator %s missing __instancecheck__' % self.__class__.__name__)


class NumberInRange(Validator):
  _min_value: float = float('-inf')
  _max_value: float = float('inf')

  def __init__(
      self,
      min_value: Optional[Number] = None,
      max_value: Optional[Number] = None):
    if min_value is None and max_value is None:
      raise ValueError('min_value and max_value are both None')
    elif (min_value is not None and max_value is not None and
        type(min_value) != type(max_value)):
      raise ValueError('type of min_value (%s) and max_value (%s) must match' %
                       (type(min_value), type(max_value)))
    if min_value is not None:
      self._base_type = type(min_value)
      self._min_value = min_value
    if max_value is not None:
      self._base_type = type(max_value)
      self._max_value = max_value

  def __instancecheck__(self, obj: Any) -> bool:
    if not self._base_type.__instancecheck__(obj):
      return False
    return self._min_value <= obj <= self._max_value

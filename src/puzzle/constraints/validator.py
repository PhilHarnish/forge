import numbers
import re
from typing import Any, List, Optional, Union


_COLOR_REGEX = re.compile('^(?:#)?([A-Fa-f0-9]{1,8})$')


class Validator(object):
  base_class: type
  __name__: str

  def __init__(self, base_class: type):
    self.base_class = base_class
    self.__name__ = self.__class__.__name__  # Emulate a `type`.

  def __call__(self, *args, **kwargs) -> None:
    return None  # Fool runtime checks in typing module.

  def __instancecheck__(self, instance: Any) -> bool:
    return isinstance(instance, self.base_class)

  def __repr__(self) -> str:
    return '%s(%s)' % (self.__class__.__name__, self._args())

  def _args(self) -> str:
    return ''


class NumberInRange(Validator):
  min_value: numbers.Number = float('-inf')
  max_value: numbers.Number = float('inf')

  def __init__(
      self,
      min_value: Optional[numbers.Number] = None,
      max_value: Optional[numbers.Number] = None):
    if min_value is None and max_value is None:
      raise ValueError('min_value and max_value are both None')
    if min_value is not None:
      self.min_value = min_value
    if max_value is not None:
      self.max_value = max_value
    super().__init__(numbers.Number)

  def __instancecheck__(self, instance: Any) -> bool:
    if not super().__instancecheck__(instance):
      return False
    return self.min_value <= instance <= self.max_value

  def _args(self) -> str:
    return 'min_value=%s, max_value=%s' % (self.min_value, self.max_value)


ColorChannel = NumberInRange(min_value=0, max_value=255)


class Color(Validator):
  def __init__(self, n_channels: int = 1, flat: bool = True) -> None:
    if flat and n_channels != 1:
      raise NotImplementedError('Unable to flatten %d channels' % n_channels)
    super().__init__(int)
    self._n_channels = n_channels
    self._flat = flat

  def coerce(
      self, value: Any, flat: Optional[bool] = None) -> Union[int, List[int]]:
    if flat is None:
      flat = self._flat
    result = []
    if isinstance(value, (tuple, list)):
      result = value
    elif isinstance(value, ColorChannel):
      value = int(value)
      result = [value] * self._n_channels
    elif isinstance(value, str):
      matched = _COLOR_REGEX.match(value)
      if matched:
        value = matched.group(1)
      if not matched or not value:
        pass  # Error handling below.
      elif len(value) in (3, 4):  # Double before reading each channel.
        result = [int(v * 2, 16) for v in value]
      elif len(value) in (1, 2, 4, 6, 8):
        result = [
          int(value[start:start+2], 16) for start in range(0, len(value), 2)
        ]
    if not result:
      pass
    elif flat:
      if len(result) == 1:
        return result[0]
      elif all(value == result[0] for value in result):  # Monochrome: #9f9f9f.
        return result[0]
    elif len(result) == 1:  # Monochrome.
      return result * self._n_channels
    elif len(result) == self._n_channels:
      return result
    elif self._n_channels == 1 and all(value == result[0] for value in result):
      return [result[0]]
    raise ValueError(
        '"%s" is not a %d-channel color' % (value, self._n_channels))

  def to_rgb_hex(self, value: Any) -> str:
    coerced = self.coerce(value, flat=False)
    if len(coerced) == 1:
      return '#%0.2x%0.2x%0.2x' % (coerced[0], coerced[0], coerced[0])
    elif len(coerced) in (3, 4):
      return '#%0.2x%0.2x%0.2x' % tuple(coerced[:3])
    raise ValueError('Cannot hex encode "%s"' % str(coerced))

  def __instancecheck__(self, instance: Any) -> bool:
    if isinstance(instance, (tuple, list)):
      values = instance
    else:
      values = [instance]
    return all(isinstance(value, int) for value in values)


class RangeInRange(Validator):
  min_value: numbers.Number
  max_value: numbers.Number

  def __init__(
      self, min_value: numbers.Number, max_value: numbers.Number) -> None:
    self.min_value = min_value
    self.max_value = max_value
    super().__init__(list)

  def __instancecheck__(self, instance: Any) -> bool:
    if not super().__instancecheck__(instance) or len(instance) != 2:
      return False
    min_value, max_value = instance
    return self.min_value <= min_value <= max_value <= self.max_value

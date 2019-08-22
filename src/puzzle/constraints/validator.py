import enum
import numbers
from typing import Any, Optional


class Validator(object):
  base_class: type

  def __init__(self, base_class: type):
    self.base_class = base_class

  def __call__(self, *args, **kwargs) -> None:
    return None  # Fool runtime checks in typing module.

  def __instancecheck__(self, instance: Any) -> bool:
    return isinstance(instance, self.base_class)

  def __repr__(self) -> str:
    return '%s(%s)' % (self.__class__.__name__, self._args())

  def _args(self) -> str:
    return ''


class Enum(Validator):
  def __init__(self, base_class: type):
    if not issubclass(base_class, enum.Enum):
      raise TypeError('Validator.Enum requires an enum.Enum (%s given)' % (
          base_class.__name__))
    super().__init__(base_class)

  def _args(self) -> str:
    return 'base_class=%s()' % self.base_class.__name__


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

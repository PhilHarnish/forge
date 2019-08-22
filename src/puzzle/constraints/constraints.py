"""
Constraints validate value matches specified type before assigning.

Constraints are:
* Optional or required
* May have one or more values
"""

from typing import Any, Generic, Iterable, NamedTuple, Optional, \
  Tuple, Union

from rx import subjects

from data import types
from puzzle.constraints import validator

Constraint = Union[validator.Validator, type]


class ConstraintChangeEvent(NamedTuple):
  constraints: 'Constraints'
  key: str
  previous: Any
  current: Any


# Find penultimate class from typing module. ("object" is final base class.)
_TYPING_BASES = (type(Union).mro()[-2], Generic)


class Constraints(object):
  _subject: subjects.Subject = None

  def __init__(self) -> None:
    self._subject = subjects.Subject()

  def subscribe(self, observer: types.Observer):
    self._subject.subscribe(observer)

  def is_modifiable(self, key: str) -> bool:
    del key
    return True

  def _is_internal(self, key: str) -> bool:
    if not hasattr(self, key):
      raise AttributeError('%s not in %s' % (key, self.__class__.__name__))
    return key.startswith('_')  # Hide private properties.

  def __iter__(self) -> Iterable[Tuple[str, Any, type]]:
    for key in sorted(dir(self)):
      if self._is_internal(key):
        continue
      annotation = _resolve_annotation(type(self), key)
      if annotation:
        yield key, getattr(self, key), annotation

  def __setattr__(self, key: str, value: Any) -> None:
    if self._is_internal(key):
      object.__setattr__(self, key, value)
      return
    annotation = self._resolve_annotation(key)
    if not annotation:
      raise AttributeError('%s not in %s' % (key, self.__class__.__name__))
    if not _type_check(value, annotation):
      raise ValueError('%s.%s must be %s (%s given)' % (
          self.__class__.__name__, key, annotation, value,
      ))
    if not self.is_modifiable(key):
      raise AttributeError('%s is not modifiable' % key)
    previous = object.__getattribute__(self, key)
    if previous != value:
      object.__setattr__(self, key, value)
      self._subject.on_next(ConstraintChangeEvent(self, key, previous, value))

  def __str__(self) -> str:
    return '\n'.join('%s = %s' % (key, repr(value)) for key, value, _ in self)

  def _resolve_annotation(self, k: str) -> Optional[type]:
    return _resolve_annotation(self.__class__, k)


def unwrap_optional(annotation: type) -> Optional[type]:
  if (not isinstance(annotation, type(Union)) or
      not hasattr(annotation, '__args__')):
    return None
  args = getattr(annotation, '__args__')
  if len(args) != 2:
    return None
  return next(a for a in args if a is not type(None))  # First non-None value.


def _type_check(value: Any, annotation: type) -> bool:
  if (not isinstance(annotation, _TYPING_BASES) or
      not hasattr(annotation, '__args__')):
    return isinstance(value, annotation)
  args = getattr(annotation, '__args__')  # E.g. "a, b, c" in Union[a, b, c].
  if isinstance(annotation, type(Union)):
    # With Union, any of the arguments are valid.
    # NB: `Optional` is an alias for Union.
    return any(_type_check(value, a) for a in args)
  elif isinstance(annotation, type(Tuple)):
    return isinstance(value, tuple) and len(value) == len(args) and all(
        _type_check(v, a) for v, a in zip(value, args))
  elif isinstance(annotation, type(Iterable)):
    if (hasattr(annotation, '__extra__') and
        not isinstance(value, getattr(annotation, '__extra__'))):
      return False  # E.g., __extra__ is `list` for typing.List.
    try:
      sample_value = next(iter(value))
      return any(_type_check(sample_value, a) for a in args)
    except TypeError:
      return False
  return False


def _resolve_annotation(cls: type, k: str) -> Optional[type]:
  for klass in cls.mro():
    if not hasattr(klass, '__annotations__') or k not in klass.__annotations__:
      continue
    return klass.__annotations__[k]
  return None

"""
Constraints validate value matches specified type before assigning.

Constraints are:
* Optional or required
* May have one or more values
"""

from typing import Any, Generic, Iterable, Tuple, Union

# Find penultimate class from typing module. ("object" is final base class.)
_TYPING_BASES = (type(Union).mro()[-2], Generic)

class Constraints(object):
  def __setattr__(self, key: str, value: Any) -> None:
    annotation = _resolve_annotation(self.__class__, key)
    if not _type_check(value, annotation):
      raise ValueError('%s.%s must be %s (%s given)' % (
          self.__class__.__name__, key, annotation, value,
      ))
    object.__setattr__(self, key, value)


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


def _resolve_annotation(cls: type, k: str) -> type:
  for klass in cls.mro():
    if k not in klass.__annotations__:
      continue
    return klass.__annotations__[k]
  raise AttributeError('%s not in %s' % (k, cls.__name__))

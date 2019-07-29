"""
Constraints validate value matches specified type before assigning.

Constraints are:
* Optional or required
* May have one or more values
"""

from typing import Any, Iterable, Union


class Constraints(object):
  def __setattr__(self, k: str, v: Any) -> None:
    types = _resolve_types(self.__class__, k)
    if not isinstance(v, types):
      raise ValueError('%s.%s must be %s (%s given)' % (
          self.__class__.__name__, k, types, v
      ))
    object.__setattr__(self, k, v)


def _resolve_types(cls: type, k: str) -> Union[type, Iterable[type]]:
  for klass in cls.mro():
    if k not in klass.__annotations__:
      continue
    t = klass.__annotations__[k]
    if isinstance(t, type(Union)):
      return t.__args__
    return t
  raise AttributeError('%s not in %s' % (k, cls.__name__))

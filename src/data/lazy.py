from typing import Any, Callable, TypeVar

T = TypeVar('T')


def prop(fn: Callable[[Any], T]) -> property:
  attr_name = '__cached__' + fn.__name__

  @property
  def wrapped(self: Any) -> T:
    if not hasattr(self, attr_name):
      setattr(self, attr_name, fn(self))
    return getattr(self, attr_name)

  return wrapped

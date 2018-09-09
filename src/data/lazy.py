import typing


def prop(fn: typing.Callable[[typing.Any], typing.Any]):
  attr_name = '__cached__' + fn.__name__

  @property
  def prop(self: typing.Any) -> typing.Any:
    if not hasattr(self, attr_name):
      setattr(self, attr_name, fn(self))
    return getattr(self, attr_name)

  return prop

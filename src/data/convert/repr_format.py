from typing import Any


def as_args(*args: Any, **kwargs: Any) -> str:
  return ', '.join([
                     repr(arg) for arg in args
                   ] + [
                     '%s=%s' % (key, repr(value)) for key, value in
                     sorted(kwargs.items(), key=lambda x: x[0])
                   ])

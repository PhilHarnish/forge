from typing import Any

import numpy as np

_DEFAULT_NDARRAY_DTYPE = np.array(()).dtype


def as_args(*args: Any, **kwargs: Any) -> str:
  return ', '.join([
                     repr_value(arg) for arg in args
                   ] + [
                     '%s=%s' % (key, repr_value(value)) for key, value in
                     sorted(kwargs.items(), key=lambda x: x[0])
                   ])


def repr_ndarray(value: np.ndarray) -> str:
  args = []
  if np.all(value == 0):
    fn = 'zeros'
    args.append(repr(value.shape))
  elif np.all(value == 1):
    fn = 'ones'
    args.append(repr(value.shape))
  else:
    fn = 'array'
    args.append('shape=%s' % repr(value.shape))
  if value.dtype != _DEFAULT_NDARRAY_DTYPE:
    args.append('dtype=np.%s' % value.dtype)
  return 'np.%s(%s)' % (fn, ', '.join(args))


def repr_value(value: Any) -> str:
  if isinstance(value, np.ndarray):
    return repr_ndarray(value)
  return repr(value)

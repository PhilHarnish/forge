import collections

from data.logic import _dimension_slice


class _DimensionFactory(object):
  def __init__(self):
    self._dimensions = {}

  def __call__(self, **kwargs):
    if not kwargs:
      raise TypeError('kwarg is required')
    elif len(kwargs) > 1:
      raise TypeError('Register only one dimension at a time (%s given)' % (
        ', '.join(kwargs.keys())))
    for dimension, values in kwargs.items():
      if dimension in self._dimensions:
        raise TypeError('Dimension %s already registered to %s' % (
          dimension, self._dimensions[dimension]
        ))
      self._dimensions[dimension] = self._make_slices(dimension, values)
      return self._dimensions[dimension].values()
    raise TypeError('invalid call %s' % kwargs)

  def _make_slices(self, dimension, values):
    result = collections.OrderedDict()
    for slice in values:
      result[slice] = _dimension_slice._DimensionSlice(self, {dimension: slice})
    return result

  def resolve(self, slice, key):
    raise KeyError('dimension key "%s" is unknown' % key)

  def dimensions(self):
    return self._dimensions

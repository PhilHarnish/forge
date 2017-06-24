import collections

from data.logic import _dimension_slice


class _DimensionFactory(object):
  def __init__(self):
    self._dimensions = collections.OrderedDict()
    self._id_to_dimension = {}
    self._slice_cache = {}

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
      for value in values:
        if value in self._dimensions:
          raise TypeError('ID %s collides with dimension of same name' % (
            value))
        if value in self._id_to_dimension:
          raise TypeError('ID %s already reserved by %s' % (
            value, self._id_to_dimension[value]))
        self._id_to_dimension[value] = dimension
      return self._dimensions[dimension].values()
    raise TypeError('invalid call %s' % kwargs)

  def _make_slices(self, dimension, values):
    result = collections.OrderedDict()
    for value in values:
      result[value] = _dimension_slice._DimensionSlice(self, {dimension: value})
    return result

  def resolve(self, slice, key):
    value = None
    if key in self._dimensions:
      dimension = key
    elif key in self._id_to_dimension:
      dimension = self._id_to_dimension[key]
      value = key
    else:
      raise KeyError('dimension key "%s" is unknown' % key)
    address = slice.dimension_address()
    if dimension not in address or address[dimension] is None:
      address = {
        dimension: value,
      }
      address.update(slice.dimension_address())
      return self._get_slice(address)
    else:
      raise KeyError('slice already constrained %s to %s' % (
        dimension, slice._constraints[dimension]))

  def dimension_address_name(self, address):
    key_parts = []
    for dimension in self._dimensions:
      if dimension in address:
        key_parts.append('%s["%s"]' % (dimension, address[dimension]))
    return '.'.join(key_parts)

  def _get_slice(self, address):
    key = self.dimension_address_name(address)
    if key not in self._slice_cache:
      self._slice_cache[key] = _dimension_slice._DimensionSlice(self, address)
    return self._slice_cache[key]

  def dimensions(self):
    return self._dimensions

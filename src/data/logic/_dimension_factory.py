import collections
import itertools

from data.logic import _dimension_slice, _util


class _DimensionFactory(_dimension_slice._DimensionSlice):
  def __init__(self):
    super(_DimensionFactory, self).__init__(self, {})
    self._dimensions = collections.OrderedDict()
    # Map of identifier: dimension.
    self._id_to_dimension = {}
    # Cache of already-requested dimensions.
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
      return _OriginalDimensionSlice(
          self, {dimension: None}, self._dimensions[dimension].values())
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
    address = slice.dimension_constraints()
    if dimension not in address or address[dimension] is None:
      address = address.copy()
      address[dimension] = value
      return self._get_slice(address)
    else:
      raise KeyError('slice already constrained %s to %s' % (
        dimension, slice._constraints[dimension]))

  def _get_slice(self, constraints):
    address = _util.address(self._dimensions, constraints)
    if address not in self._slice_cache:
      self._slice_cache[address] = _dimension_slice._DimensionSlice(self,
          constraints)
    return self._slice_cache[address]

  def dimensions(self):
    return self._dimensions

  def cardinality_groups(self):
    result = []
    for (x_key, x_values), (y_key, y_values) in itertools.combinations(
        self._dimensions.items(), 2):
      constraint = {}
      # Rows.
      for x_value in x_values:
        constraint[x_key] = x_value
        group = []
        result.append(group)
        for y_value in y_values:
          constraint[y_key] = y_value
          group.append(constraint.copy())
      # Columns.
      for y_value in y_values:
        constraint[y_key] = y_value
        group = []
        result.append(group)
        for x_value in x_values:
          constraint[x_key] = x_value
          group.append(constraint.copy())
    return result


class _OriginalDimensionSlice(_dimension_slice._DimensionSlice):
  def __init__(self, factory, constraints, children):
    super(_OriginalDimensionSlice, self).__init__(factory, constraints)
    self._children = children

  def __iter__(self):
    return iter(self._children)

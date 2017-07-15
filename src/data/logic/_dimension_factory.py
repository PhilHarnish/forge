import collections
import itertools

from data.logic import _dimension_slice, _util


class _DimensionFactory(_dimension_slice._DimensionSlice):
  def __init__(self):
    super(_DimensionFactory, self).__init__(self, {})
    self._dimensions = collections.OrderedDict()
    # Map of dimension: size (range of accepted values, including duplicates).
    self._dimension_size = {}
    # Map of identifier: dimension.
    self._value_to_dimension = {}
    # Map of value: cardinality (number of duplicates).
    self._value_cardinality = collections.defaultdict(int)
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
        raise TypeError('Dimension "%s" already registered to %s' % (
          dimension, self._dimensions[dimension]
        ))
      self._dimensions[dimension] = self._make_slices(dimension, values)
      dimension_size = len(values)
      self._dimension_size[dimension] = dimension_size
      max_dimension_size = max(self._dimension_size.values())
      if dimension_size < max_dimension_size:
        # There could be up to `max_dimension_size` duplicates.
        max_cardinality = max_dimension_size
      else:
        max_cardinality = 1
      child_dimensions = []
      for value in values:
        if value in self._dimensions:
          raise TypeError('ID %s collides with dimension of same name' % (
            value))
        if (value in self._value_to_dimension and
            dimension != self._value_to_dimension[value]):
          raise TypeError('ID %s already reserved by %s' % (
              value, self._value_to_dimension[value]))
        self._value_to_dimension[value] = dimension
        self._value_cardinality[value] += 1
        child_dimensions.append(self._dimensions[dimension][value])
      for value in values:
        self._value_cardinality[value] = max(
            max_cardinality, self._value_cardinality[value])
      return _OriginalDimensionSlice(self, {dimension: None}, child_dimensions)
    raise TypeError('invalid call %s' % kwargs)

  def _make_slices(self, dimension, values):
    result = collections.OrderedDict()
    for value in values:
      # Cannot use _get_slice here as it depends on address which requires
      # a populated cache.
      result[value] = _dimension_slice._DimensionSlice(self, {dimension: value})
    return result

  def resolve(self, slice, key):
    """Finds the best sub-slice of `slice` for `key`."""
    value = None
    if key in self._dimensions:
      dimension = key
    elif key in self._value_to_dimension:
      dimension = self._value_to_dimension[key]
      value = key
    else:
      raise KeyError('dimension key "%s" is unknown' % key)
    constraints = slice.dimension_constraints()
    if dimension not in constraints or constraints[dimension] is None:
      constraints = constraints.copy()
      constraints[dimension] = value
      return self._get_slice(constraints)
    elif value is None:
      return constraints[dimension]
    else:
      raise KeyError('slice already constrained %s to %s' % (
        dimension, slice._constraints[dimension]))

  def resolve_all(self, slice):
    template_constraints = {}
    free_dimensions = []
    for key, value in slice.dimension_constraints().items():
      if value is None:
        free_dimensions.append(key)
      else:
        template_constraints[key] = value
    if not free_dimensions:
      return [slice]
    elif len(free_dimensions) > 1:
      # Currently no known legitimate use case for multiple free dimensions.
      # "Correct" implementation impossible without a reference use case.
      raise KeyError('resolving multiple free dimensions')
    children = []
    for dimension in free_dimensions:
      for value in self._dimensions[dimension]:
        template_constraints[dimension] = value
        children.append(self._get_slice(template_constraints.copy()))
    return children

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
      if self._dimension_size[x_key] >= self._dimension_size[y_key]:
        # Rows: there are more (or equal) x values than y values.
        # This implies y values should not repeat for this row.
        for x_value in x_values:
          constraint[x_key] = x_value
          group = []
          cardinality = self._value_cardinality[x_value]
          result.append((group, cardinality))
          for y_value in y_values:
            constraint[y_key] = y_value
            group.append(constraint.copy())
      if self._dimension_size[y_key] >= self._dimension_size[x_key]:
        # Rows: there are more (or equal) y values than x values.
        # This implies x values should not repeat for this column.
        for y_value in y_values:
          constraint[y_key] = y_value
          group = []
          cardinality = self._value_cardinality[y_value]
          result.append((group, cardinality))
          for x_value in x_values:
            constraint[x_key] = x_value
            group.append(constraint.copy())
    return result

  def inference_groups(self):
    """Aligned cells between 3 boards must not sum to 2.

    Consider: Andy is 10, 10's favorite color is red -> Andy's is red. This
    inference holds for: (a) 0 are True, (b) 1 is True, OR (c) all 3 True.
    Therefore 0, 1, and 3 are valid sums for the 3 aligned relationships.

    Each board triplet inference is computed like so:
      y y  z z
    x A1A2 B1B2  A1 + B1 + C1 != 2 -- A, top left #1
    x A3A4 B3B4  A1 + B2 + C3 != 2 -- A, top left #2
    z C1C2       A2 + B1 + C2 != 2 -- A, top right, #1
    z C3C4       A2 + B2 + C4 != 2 -- A, top right, #2
    """
    result = []
    visited_triplets = set()
    for x, y, z in itertools.combinations(self._dimensions.items(), 3):
      (x_key, x_values), (y_key, y_values), (z_key, z_values) = x, y, z
      board_a = (x_key, y_key)
      board_b = (x_key, z_key)
      board_c = (y_key, z_key)
      triplet = ','.join(map(str, sorted([board_a, board_b, board_c])))
      if triplet in visited_triplets:
        raise Exception('Redundant work performed?')
      visited_triplets.add(triplet)
      # Prefetch all of the rows from board B and columns from board C as they
      # will be needed repeatedly.
      rows = []
      for x_value in x_values:
        row = []
        rows.append(row)
        x_value_cardinality = self._value_cardinality[x_value]
        for z_value in z_values:
          slice_cardinality = (
            x_value_cardinality * self._value_cardinality[z_value])
          row.append(({
            x_key: x_value,
            z_key: z_value,
          }, slice_cardinality))
      columns = []
      for y_value in y_values:
        column = []
        columns.append(column)
        y_value_cardinality = self._value_cardinality[y_value]
        for z_value in z_values:
          slice_cardinality = (
            y_value_cardinality * self._value_cardinality[z_value])
          column.append(({
            y_key: y_value,
            z_key: z_value,
          }, slice_cardinality))
      # For each cell in board A set up inference with aligned rows and columns.
      for row_index, x_value in enumerate(x_values):
        x_value_cardinality = self._value_cardinality[x_value]
        for column_index, y_value in enumerate(y_values):
          y_value_cardinality = self._value_cardinality[y_value]
          slice_cardinality = x_value_cardinality * y_value_cardinality
          assert len(rows[row_index]) == len(columns[column_index])
          for row, column in zip(rows[row_index], columns[column_index]):
            # A1 + B1 + C1 != 2 -- A, top left #1  (see doc above).
            result.append((
              ({x_key: x_value, y_key: y_value}, slice_cardinality),
              row,
              column,
            ))
    return result

  def value_cardinality(self, value):
    return self._value_cardinality[value]


class _OriginalDimensionSlice(_dimension_slice._DimensionSlice):
  """Similar to _DimensionSlice except it remembers duplicate values.

  Normally, dimension factory (and user code) has no use for redundantly
  iterating duplicate values. However, when a dimension is created this syntax
  is expected to work:
      red, green, red, green = factory(color=['red', 'green', 'red', 'green'])
  """

  def __init__(self, factory, constraints, children):
    super(_OriginalDimensionSlice, self).__init__(factory, constraints)
    self._children = children

  def __iter__(self):
    return iter(self._children)

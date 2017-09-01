import collections
import itertools

from data.logic import _dimension_slice, _util

Cardinality = collections.namedtuple(
    'Cardinality', field_names=['group', 'cardinality'])
TotalCardinality = collections.namedtuple(
    'TotalCardinality', field_names=['group', 'total'])
UniqueCardinality = collections.namedtuple(
    'UniqueCardinality', field_names=['group'])
CardinalityRange = collections.namedtuple(
    'CardinalityRange',
    field_names=['group', 'min_cardinality', 'max_cardinality'])
Inference = collections.namedtuple(
    'Inference', field_names=['group', 'cardinalities'])
ValueSumsInference = collections.namedtuple(
    'ValueSumsInference', field_names=['groups', 'scores'])


class _DimensionFactory(_dimension_slice._DimensionSlice):
  def __init__(self):
    super(_DimensionFactory, self).__init__(self, {})
    self._dimensions = collections.OrderedDict()
    # Set of dimensions which can be optimized to compact scalars.
    self._compact_dimensions = set()
    # Map of dimension: size (range of accepted values, including duplicates).
    self._dimension_size = {}
    # Maximum dimension size seen. Largest dimension should be first.
    self._max_dimension_size = 0
    # Map of identifier: dimension.
    self._value_to_dimension = {}
    # Map of value: min cardinality (min number of duplicates).
    self._min_value_cardinality = collections.defaultdict(int)
    # Map of value: max cardinality (max number of duplicates).
    self._max_value_cardinality = collections.defaultdict(int)
    # Cache of already-requested dimensions.
    self._slice_cache = {}

  def __call__(self, *args, **kwargs):
    if bool(args) == bool(kwargs):
      raise TypeError('args OR kwarg is required')
    elif len(kwargs) > 1:
      raise TypeError('Register only one dimension at a time (%s given)' % (
        ', '.join(kwargs.keys())))
    dimensions = list(args) + list(kwargs.items())
    dimension = '_'.join(name for name, values in dimensions)
    if dimension in self._dimensions:
      raise TypeError('Dimension "%s" already registered to %s' % (
        dimension, self._dimensions[dimension]
      ))
    inputs = list(values for name, values in dimensions)
    # A list of (id, source) tuples.
    values = []
    for input in itertools.product(*inputs):
      if len(input) > 1:
        values.append((''.join(map(str, input)), input))
      else:
        values.append((input[0], input))
    self._dimensions[dimension] = self._make_slices(dimension, values)
    dimension_size = len(values)
    self._dimension_size[dimension] = dimension_size
    if not self._max_dimension_size:
      # Use first dimension to establish max dimension size.
      # Apparently, future dimensions can be larger without breaking later
      # assumptions.
      self._max_dimension_size = dimension_size
    if dimension_size < self._max_dimension_size:
      # At least one of each `dimension_size` must be chosen, after which this
      # value may be chosen repeatedly. For example, if max is 7 and this
      # dimension size is 3 then either choice can be up to 5.
      max_cardinality = self._max_dimension_size - (dimension_size - 1)
    else:
      max_cardinality = 1
    child_dimensions = []
    duplicates = False
    for value, source in values:
      if value in self._dimensions:
        raise TypeError('ID %s collides with dimension of same name' % (
          value))
      if value in self._value_to_dimension:
        duplicates = True
        if dimension != self._value_to_dimension[value]:
          raise TypeError('ID %s already reserved by %s' % (
              value, self._value_to_dimension[value]))
      self._value_to_dimension[value] = dimension
      self._min_value_cardinality[value] += 1
      self._max_value_cardinality[value] += 1
      child_dimensions.append((self._dimensions[dimension][value], set(source)))
    for value, _ in values:
      self._max_value_cardinality[value] = max(
          max_cardinality, self._max_value_cardinality[value])
    raw_values = [i for i, _ in values]
    if (not duplicates and all(isinstance(i, int) for i in raw_values) and
        raw_values == list(range(raw_values[0], raw_values[-1] + 1))):
      self._compact_dimensions.add(dimension)
    if len(inputs) == 1:
      return _dimension_slice._OriginalDimensionSlice(
          self, {dimension: None}, child_dimensions)
    return [_dimension_slice._DimensionFilterSlice(
        self, {dimension: None}, child_dimensions)] * len(inputs)

  def _make_slices(self, dimension, values):
    result = collections.OrderedDict()
    for value, _ in values:
      # Cannot use _get_slice here as it depends on address which requires
      # a populated cache.
      result[value] = _dimension_slice._DimensionSlice(self, {dimension: value})
    return result

  def resolve(self, slice, key):
    """Finds the best sub-slice of `slice` for `key`."""
    value = None
    if isinstance(key, _dimension_slice._DimensionSlice):
      if len(key) > 1:
        raise KeyError(
            'Attempted to resolve multiple dimensions at once: %s',
            key.dimension_constraints())
      dimension, value = list(key.dimension_constraints().items())[0]
    elif key in self._dimensions:
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

  def compact_dimensions(self, x, y):
    """Analyzes x, y dimensions to decide if they should be compacted.

    Returns:
      (compact, swap). If `swap` is True then x is the dimension compacted.
    """
    if len(self._dimensions) > 3:
      # Do not attempt compaction for so many dimensions. Inference breaks down.
      return False, False
    if (self._dimension_size[x] == self._dimension_size[y] and
        len(self._dimensions[x]) == len(self._dimensions[y])):
      # Only attempt to use compacted dimensions when the two dimensions are
      # both the same size, without duplicates.
      if x in self._compact_dimensions:
        return True, True
      return y in self._compact_dimensions, False
    return False, False

  def dimension_constraint_groups(self):
    result = []
    # Constraints for rows and columns within a sub-grid.
    self._append_cardinality_groups(result)
    # Constraints for sub-grids.
    self._append_group_sums(result)
    # Constraints for values between 3 grids (AxB, BxC, AxC).
    self._append_inference_groups(result)
    # Constraints for values between row of grids (AxB, AxC, AxD, ...).
    self._append_value_sums_inference(result)
    return result

  def _append_cardinality_groups(self, result=None):
    if result is None:
      result = []
    for (x_key, x_values), (y_key, y_values) in itertools.combinations(
        self._dimensions.items(), 2):
      compact, swap = self.compact_dimensions(x_key, y_key)
      # Only attempt to use compacted dimensions when the two dimensions are
      # both the same size, without duplicates.
      if swap:
        (x_key, x_values), (y_key, y_values) = (y_key, y_values), (x_key, x_values)
      if compact:
        constraint = {
          y_key: None,
        }
        group = []
        result.append(UniqueCardinality(group))
        for x_value in x_values:
          constraint[x_key] = x_value
          group.append(constraint.copy())
      else:
        # Rows.
        self._append_cardinality_group(result, x_key, x_values, y_key, y_values)
        # Columns.
        self._append_cardinality_group(result, y_key, y_values, x_key, x_values)
    return result

  def _append_cardinality_group(
      self, result, major_key, major_values, minor_key, minor_values):
    #if self._dimension_size[major_key] < self._dimension_size[minor_key]:
    #  return  # Handle when keys are reversed.
    for major_value in major_values:
      min_cardinality = self._min_value_cardinality[major_value]
      max_cardinality = self._max_value_cardinality[major_value]
      group = []
      for minor_value in minor_values:
        group.append({
          major_key: major_value,
          minor_key: minor_value,
        })
      #if major_key in ('omelet', 'pancake') and minor_key in ('omelet', 'pancake'):
      #  print('wat')
      if min_cardinality == max_cardinality:
        result.append(Cardinality(group, min_cardinality))
      else:
        result.append(CardinalityRange(group, min_cardinality, max_cardinality))

  def _append_inference_groups(self, result=None):
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
    if result is None:
      result = []
    for x, y, z in itertools.combinations(self._dimensions.items(), 3):
      (x_key, x_values), (y_key, y_values), (z_key, z_values) = x, y, z
      # Prefetch all of the rows from board B and columns from board C as they
      # will be needed repeatedly.
      rows = []
      for x_value in x_values:
        row = []
        rows.append(row)
        x_value_cardinality = self._max_value_cardinality[x_value]
        for z_value in z_values:
          slice_cardinality = (
            x_value_cardinality * self._max_value_cardinality[z_value])
          row.append(({
            x_key: x_value,
            z_key: z_value,
          }, slice_cardinality))
      columns = []
      for y_value in y_values:
        column = []
        columns.append(column)
        y_value_cardinality = self._max_value_cardinality[y_value]
        for z_value in z_values:
          slice_cardinality = (
            y_value_cardinality * self._max_value_cardinality[z_value])
          column.append(({
            y_key: y_value,
            z_key: z_value,
          }, slice_cardinality))
      # For each cell in board A set up inference with aligned rows and columns.
      for row_index, x_value in enumerate(x_values):
        x_value_cardinality = self._max_value_cardinality[x_value]
        for column_index, y_value in enumerate(y_values):
          y_value_cardinality = self._max_value_cardinality[y_value]
          slice_cardinality = x_value_cardinality * y_value_cardinality
          assert len(rows[row_index]) == len(columns[column_index])
          for row, column in zip(rows[row_index], columns[column_index]):
            # Sort groups by slice_cardinality, smallest first.
            group = list(sorted([
              ({x_key: x_value, y_key: y_value}, slice_cardinality),
              row,
              column,
            ], key=lambda i: i[1]))
            # A1 + B1 + C1 != 2 -- A, top left #1  (see doc above).
            result.append(Inference(
              [group[0][0], group[1][0], group[2][0]],
              [group[0][1], group[1][1], group[2][1]],
            ))
    return result

  def _append_group_sums(self, result):
    for (x_key, x_values), (y_key, y_values) in itertools.combinations(
        self._dimensions.items(), 2):
      if (self._max_dimension_size == self._dimension_size[x_key] or
          self._max_dimension_size == self._dimension_size[y_key]):
        continue
      group = []
      result.append(TotalCardinality(group, self._max_dimension_size))
      for x, y in itertools.product(x_values, y_values):
        group.append({
          x_key: x,
          y_key: y,
        })
    return result

  def _append_value_sums_inference(self, result):
    """Sum of grid values along a column should always match."""
    for primary_key, primary_values in self._dimensions.items():
      if self._dimension_size[primary_key] == self._max_dimension_size:
        # A well-constrained dimension doesn't need sum inference.
        continue
      for primary_value in primary_values:
        groups = []
        scores = []
        for secondary_key, secondary_values in self._dimensions.items():
          score = 0
          if primary_key == secondary_key:
            continue
          elif self._dimension_size[secondary_key] == self._max_dimension_size:
            # This is a good reference.
            score = 1
          group = []
          has_duplicate = False
          for secondary_value in secondary_values:
            if self._max_value_cardinality[secondary_value] > 1:
              has_duplicate = True
            group.append({
              primary_key: primary_value,
              secondary_key: secondary_value,
            })
          if not has_duplicate:
            score = 2
          groups.append(group)
          scores.append(score)
        if len(groups) <= 1:
          continue
        result.append(ValueSumsInference(groups, scores))
    return result

  def value_cardinality(self, value):
    return self._max_value_cardinality[value]

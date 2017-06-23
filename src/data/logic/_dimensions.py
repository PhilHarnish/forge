import itertools

import Numberjack


class _DimensionSlice(dict):
  def __init__(self, dimensions, storage_order, id_to_dimension, data):
    super(_DimensionSlice, self).__init__()
    self._dimensions = dimensions
    self._storage_order = storage_order
    self._id_to_dimension = id_to_dimension
    self._data = data
    self._constraints = []
    self._slice_constraints = {}

  def __copy__(self):
    slice = _DimensionSlice(
        self._dimensions, self._storage_order, self._id_to_dimension,
        self._data)
    slice._constraints = self._constraints
    slice._slice_constraints = self._slice_constraints.copy()
    return slice

  def __getitem__(self, item):
    if item in self._dimensions:
      return self._reify_dimension(item)
    slice = self.__copy__()
    dimension = self._id_to_dimension[item]
    if dimension in slice._slice_constraints:
      raise KeyError(
          'Unable to constrain %s = %s, already constrained to %s' % (
            dimension, item, slice._slice_constraints[dimension]))
    slice._slice_constraints[dimension] = item
    return slice

  def __setitem__(self, key, value):
    for item in self[key]:
      self._constraints.append(item == value)

  def __iter__(self):
    yield from iter(self.values())

  def values(self):
    return [v for _, v in self.items()]

  def value(self):
    values = self.values()
    if len(values) != 1:
      raise KeyError('%s values, expected 1' % len(values))
    return values[0]

  def items(self):
    n_constraints = len(self._slice_constraints)
    if n_constraints == 0:
      return self._all_slice()
    elif n_constraints < 2:
      return self._combination_slice()
    elif n_constraints == 2:
      return self._precise_slice()
    raise NotImplementedError('Querying 3+ dimensions is unsupported')

  def _all_slice(self):
    acc = []
    for dimension_x, dimension_y in itertools.combinations(
        self._storage_order, 2):
      x_values = self._dimensions[dimension_x]
      y_values = self._dimensions[dimension_y]
      for x, y in itertools.product(x_values, y_values):
        item = self._data[x][y]
        acc.append((item.name(), item))
    return acc

  def _combination_slice(self):
    acc = []
    for dimension_x, dimension_y in itertools.combinations(
        self._storage_order, 2):
      if dimension_x in self._slice_constraints:
        iter_x = [self._slice_constraints[dimension_x]]
      else:
        iter_x = self._dimensions[dimension_x]
      if dimension_y in self._slice_constraints:
        iter_y = [self._slice_constraints[dimension_y]]
      else:
        iter_y = self._dimensions[dimension_y]
      for x, y in itertools.product(iter_x, iter_y):
        item = self._data[x][y]
        acc.append((item.name(), item))
    return acc

  def _precise_slice(self):
    constraints = self._slice_constraints
    x, y = [constraints[i] for i in self._storage_order if i in constraints]
    item = self._data[x][y]
    return [(item.name(), item)]

  def _reify_dimension(self, dimension):
    if len(self._slice_constraints) != 1:
      raise KeyError()
    # Validate dimension values are all ints.
    for value in self._dimensions[dimension]:
      if not isinstance(value, int):
        raise NotImplementedError
    return Numberjack.Sum(self.values(), self._dimensions[dimension])


class _Dimensions(_DimensionSlice):
  def __init__(self, dimensions):
    storage_order = []
    id_to_dimension = {}
    data = {}
    to_add = []
    for dimension, values in sorted(
        dimensions.items(), key=lambda i: -len(i[1])):
      storage_order.append(dimension)
      to_add.append(values)
      for value in values:
        if value in id_to_dimension:
          raise Exception('Identifier %s not unique. Appears in %s and %s' % (
            value, id_to_dimension[value], dimension))
        id_to_dimension[value] = dimension
    cardinality_groups = self._init_variables(data, to_add)
    super(_Dimensions, self).__init__(
        dimensions, storage_order, id_to_dimension, data)
    self._constraints.extend(
        self._enforce_dimensional_cardinality(cardinality_groups))
    self._constraints.extend(
        self._enforce_dimensional_inference())

  def _init_variables(self, data, values):
    if not values:
      return []
    cardinality_groups = []
    if len(values) == 1:
      cardinality_groups.append([])
      for x in values[0]:
        variable = Numberjack.Variable(str(x))
        data[x] = variable
        cardinality_groups[0].append(variable)
      return cardinality_groups
    for dimension_x, dimension_y in itertools.combinations(values, 2):
      for x in dimension_x:
        data.setdefault(x, {})
        group = []
        cardinality_groups.append(group)
        for y in dimension_y:
          name = '%s_%s' % (x, y)
          variable = Numberjack.Variable(name)
          data[x][y] = variable
          group.append(variable)
      # Accumulate the inverted groups.
      for y in dimension_y:
        group = []
        cardinality_groups.append(group)
        for x in dimension_x:
          group.append(data[x][y])
    return cardinality_groups

  def _enforce_dimensional_cardinality(self, cardinality_groups):
    """Every row and column in every board should have exactly 1 True value."""
    result = []
    for group in cardinality_groups:
      num_zeros = len(group) - 1
      result.append(
          Numberjack.Gcc(group, {0: (num_zeros, num_zeros), 1: (1, 1)}))
    return result

  def _enforce_dimensional_inference(self):
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
    for dimension_x, dimension_y, dimension_z in itertools.combinations(
        self._storage_order, 3):
      board_a = (dimension_x, dimension_y)
      board_b = (dimension_x, dimension_z)
      board_c = (dimension_y, dimension_z)
      triplet = ','.join(map(str, sorted([board_a, board_b, board_c])))
      if triplet in visited_triplets:
        raise Exception('Redundant work performed?')
      visited_triplets.add(triplet)
      # Prefetch all of the rows from board B and columns from board C as they
      # will be needed repeatedly.
      rows = []
      for x in self._dimensions[dimension_x]:
        row = []
        rows.append(row)
        for z in self._dimensions[dimension_z]:
          row.append(self[x][z].value())
      columns = []
      for y in self._dimensions[dimension_y]:
        column = []
        columns.append(column)
        for z in self._dimensions[dimension_z]:
          column.append(self[y][z].value())
      # For each cell in board A set up inference with aligned rows and columns.
      for row_index, x in enumerate(self._dimensions[dimension_x]):
        for column_index, y in enumerate(self._dimensions[dimension_y]):
          assert len(rows[row_index]) == len(columns[column_index])
          for row, column in zip(rows[row_index], columns[column_index]):
            # A1 + B1 + C1 != 2 -- A, top left #1  (see doc above).
            result.append(self[x][y].value() + row + column != 2)
    return result

  def constrain(self, *constraints):
    self._constraints.extend(constraints)

  def constraints(self):
    return self._constraints

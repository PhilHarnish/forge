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

  def items(self):
    acc = []
    self._iter_items(acc, self._data, 0)
    return acc

  def _iter_items(self, acc, cursor, depth):
    if depth >= len(self._storage_order):
      acc.append((cursor.name(), cursor))
      return
    dimension = self._storage_order[depth]
    depth += 1
    if dimension in self._slice_constraints:
      self._iter_items(acc, cursor[self._slice_constraints[dimension]], depth)
    else:
      for child in self._dimensions[dimension]:
        self._iter_items(acc, cursor[child], depth)

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
        data[x] = {}
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
    result = []
    for group in cardinality_groups:
      num_zeros = len(group) - 1
      result.append(
          Numberjack.Gcc(group, {0: (num_zeros, num_zeros), 1: (1, 1)}))
    return result

  def _cardinality_groups(self):
    groups = []
    for dimension_x, dimension_y in itertools.combinations(
        self._storage_order, 2):
      group = []
      for x in self._dimensions[dimension_x]:
        for y in self._dimensions[dimension_y]:
          group.append(self._data[x])
    for dimension in self._storage_order:
      for value in self._dimensions[dimension]:
        groups.append(self[value].values())
    return groups

  def constrain(self, *constraints):
    self._constraints.extend(constraints)

  def constraints(self):
    return self._constraints

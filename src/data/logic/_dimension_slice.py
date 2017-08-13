from data.logic import _addressable_value, _ast_factory, _util


class _DimensionSlice(
    _addressable_value.AddressableValue,
    _ast_factory.AccumulatingExpressionMixin):
  def __init__(self, factory, constraints):
    self._factory = factory
    self._constraints = constraints

  def __getattr__(self, item):
    return self._factory.resolve(self, item)

  __getitem__ = __getattr__

  def __len__(self):
    return len(self._constraints)

  def __iter__(self):
    return iter(self._factory.resolve_all(self))

  def __repr__(self):
    """Evaluating dimension address locates `self` in any Logic Problem."""
    return self.dimension_address()

  def __str__(self):
    return self.dimension_address()

  def __hash__(self):
    return hash(str(self))

  def dimension_constraints(self):
    return self._constraints

  def dimension_address(self):
    return _util.address(self._factory.dimensions(), self._constraints)


class _OriginalDimensionSlice(_DimensionSlice):
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
    return iter(child for child, source in self._children)


class _DimensionFilterSlice(_OriginalDimensionSlice):
  """Adds cross-product sub-slicing to _OriginalDimensionSlice.

  Given a list of children, return a sub-slice of children.
  """
  def __init__(self, factory, constraints, children, filter=None):
    children = [(child, _normalize_ids(source)) for child, source in children]
    super(_DimensionFilterSlice, self).__init__(factory, constraints, children)
    if filter:
      self._filter = filter.copy()
    else:
      self._filter = set()

  def __getattr__(self, item):
    return _DimensionFilterSlice(
        self._factory, self._constraints, self._children,
        self._filter.union(_normalize_ids([item,])))

  __getitem__ = __getattr__

  def __iter__(self):
    needed = len(self._filter)
    results = False
    for child, source in self._children:
      if not needed or needed == len(self._filter.intersection(source)):
        yield child
        results = True
    if not results:
      raise AttributeError('No variables match %s' % self._filter)


def _normalize_ids(ids):
  result = []
  for id in ids:
    if isinstance(id, str):
      result.append(id.lower())
    else:
      result.append(id)
  return result

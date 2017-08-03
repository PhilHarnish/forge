from data.logic import _addressable_value, _ast_factory, _util


class _DimensionSlice(
    _addressable_value.AddressableValue,
    _ast_factory.AccumulatingExpressionMixin):
  def __init__(self, factory, constraints):
    self._factory = factory
    self._constraints = constraints

  def __getattr__(self, item):
    return self._factory.resolve(self, item)

  def __getitem__(self, item):
    return self._factory.resolve(self, item)

  def __len__(self):
    return len(self._constraints)

  def __iter__(self):
    return iter(self._factory.resolve_all(self))

  def __str__(self):
    return self.dimension_address()

  def __hash__(self):
    return hash(str(self))

  def dimension_constraints(self):
    return self._constraints

  def dimension_address(self):
    return _util.address(self._factory.dimensions(), self._constraints)

from data.logic import _addressable_value, _ast_factory


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

  def dimension_address(self):
    return self._constraints

  def dimension_address_name(self):
    return self._factory.dimension_address_name(self.dimension_address())

class _DimensionSlice(object):
  def __init__(self, factory, constraints):
    self._factory = factory
    self._constraints = constraints

  def __getattr__(self, item):
    return self._factory.resolve(self, item)

  def __getitem__(self, item):
    return self._factory.resolve(self, item)

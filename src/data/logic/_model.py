class _Model(object):
  def __init__(self, dimension_factory):
    self._dimension_factory = dimension_factory
    self._constraints = []

  def __call__(self, *args):
    self._constraints.extend(args)

  def constraints(self):
    return self._constraints

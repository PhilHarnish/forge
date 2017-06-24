import ast


class _Model(object):
  def __init__(self, dimension_factory):
    self._dimension_factory = dimension_factory
    self._constraints = []

  def __call__(self, *args):
    bad = list(filter(lambda i: not isinstance(i, ast.Expr), args))
    if bad:
      raise TypeError('Model only accepts expressions (given %s)' % bad)
    self._constraints.extend(args)

  def constraints(self):
    return self._constraints

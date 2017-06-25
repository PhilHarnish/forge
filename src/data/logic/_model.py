import ast

import Numberjack

from data.logic import _expr_transformer


class _Model(Numberjack.Model):
  def __init__(self, dimension_factory):
    super(_Model, self).__init__()
    self._dimension_factory = dimension_factory
    self._expr_transformer = _expr_transformer.ExprTransformer(self)
    self._constraints = []

  def __call__(self, *args):
    self.add(*args)

  def add(self, *args):
    bad = list(filter(lambda i: not isinstance(i, ast.Expr), args))
    if bad:
      raise TypeError('Model only accepts expressions (given %s)' % bad)
    super(_Model, self).add(list(self._compile(arg) for arg in args))

  def _compile(self, expr):
    return self._expr_transformer.compile(expr)

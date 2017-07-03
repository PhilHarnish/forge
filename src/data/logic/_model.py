import Numberjack

from data.logic import _expr_transformer, _reference, _util


class _Model(Numberjack.Model):
  def __init__(self, dimension_factory):
    super(_Model, self).__init__()
    self._dimension_factory = dimension_factory
    self._expr_transformer = _expr_transformer.ExprTransformer(self)
    self._variable_cache = {}
    self._constraints = []

  def __call__(self, *args):
    self.add(*args)

  def add(self, *args):
    converted = []
    for arg in args:
      if isinstance(arg, (list, tuple)):
        self.add(*arg)
      elif isinstance(arg, Numberjack.Predicate):
        converted.append(arg)
      else:
        raise TypeError('Model only accepts expressions (given %s)' % arg)
    super(_Model, self).add(converted)

  def resolve(self, address):
    return _reference.Reference(self, _util.parse(address))

  def resolve_value(self, value):
    try:
      return _reference.Reference(
          self, self._dimension_factory[value].dimension_constraints())
    except KeyError:
      # Not a specific dimension. It seems like returning "value" is possible
      # if the __r*__ operators are specified.
      return _reference.ValueReference(self, value)

import ast
import itertools

import Numberjack

from data.logic import _expr_transformer, _predicates, _reference, _util


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
      elif isinstance(arg, ast.Expr):
        converted.append(self._compile(arg))
      elif isinstance(arg, Numberjack.Predicate):
        converted.append(arg)
      else:
        raise TypeError('Model only accepts expressions (given %s)' % arg)
    super(_Model, self).add(converted)

  def _compile(self, expr):
    return self._expr_transformer.compile(expr)

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

  def get_variables(self, constraints):
    results = []
    constraint_components = constraints.items()
    # Every pair of constraints produces a variable for consideration.
    # Eg, Andy == CEO == 12 == True.
    for (key1, value1), (key2, value2) in itertools.combinations(
        constraint_components, 2):
      variable_constraints = {
        key1: value1,
        key2: value2,
      }
      address = _util.address(
          self._dimension_factory.dimensions(), variable_constraints)
      if address in self._variable_cache:
        pass
      elif value1 is not None and value2 is not None:
        # Create a boolean variable for address.
        self._variable_cache[address] = Numberjack.Variable(address)
      else:
        raise NotImplementedError()
      results.append(self._variable_cache[address])
    return _predicates.Predicates(results)

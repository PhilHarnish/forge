import ast
import itertools

import Numberjack

from data.logic import _expr_transformer, _predicates, _reference, _solver, \
  _util


class _Model(Numberjack.Model):
  def __init__(self, dimension_factory):
    super(_Model, self).__init__()
    self._dimension_factory = dimension_factory
    self._expr_transformer = _expr_transformer.ExprTransformer(self)
    self._variable_cache = {}
    self._constraints = []
    self._deferred = []

  def __call__(self, *args):
    self.add(*args)

  def add(self, *args):
    converted = []
    for arg in args:
      if isinstance(arg, (list, tuple, _predicates.Predicates)):
        self.add(*arg)
      elif isinstance(arg, ast.AST):
        self.add(self._compile(arg))
      elif isinstance(arg, Numberjack.Predicate):
        converted.append(arg)
      elif callable(arg):
        self._deferred.append(arg)
      else:
        raise TypeError('Model only accepts expressions (given "%s")' % arg)
    super(_Model, self).add(converted)

  def load(self, solvername, X=None, encoding=None):
    # WARNING: Nothing prevents redundant dimensional constraints.
    self.add(self.dimension_constraints())
    return _solver.Solver(
        self, super(_Model, self).load(solvername, X=X, encoding=encoding),
        self._deferred)

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

  def coerce_value(self, value):
    return _reference.coerce_value(value)

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
      elif value1 is None or value2 is None:
        self._variable_cache[address] = self._reify_constraints(
            variable_constraints, address)
      else:
        compact, swap = self._dimension_factory.compact_dimensions(key1, key2)
        if not compact:
          # Create a boolean variable for address.
          self._variable_cache[address] = Numberjack.Variable(address)
        elif swap:
          variable_constraints[key1] = None
          self._variable_cache[address] = (
              self.get_variables(variable_constraints) == value1)
        else:
          variable_constraints[key2] = None
          self._variable_cache[address] = (
              self.get_variables(variable_constraints) == value2)
      results.append(self._variable_cache[address])
    return _predicates.Predicates(results)

  def _reify_constraints(self, constraints, address):
    assert len(constraints) == 2
    (key1, value1), (key2, value2) = constraints.items()
    compact, swap = self._dimension_factory.compact_dimensions(key1, key2)
    if swap or value1 is None:
      # Swap values so key1/value1 are fully constrained.
      (key1, value1), (key2, value2) = (key2, value2), (key1, value1)
    assert value2 is None and value1 is not None
    values = list(self._dimension_factory.dimensions()[key2].keys())
    value_cardinality = self._dimension_factory.value_cardinality(value1)
    if compact:
      # The range of values are contiguous (i.e. no holes) and well suited for
      # a single Numberjack.Variable.
      min_value = min(values)
      max_value = max(values)
      return Numberjack.Variable(min_value, max_value, address)
    variables = []
    # These are the values which are unconstrained.
    for value in values:
      if not isinstance(value, (int, float)):
        raise TypeError('Unable to reify %s dimension, %s is not a number' % (
          key2, value))
      # Constrain to this new value, temporarily.
      constraints[key2] = value
      variables.append(self.get_variables(constraints))
    if value_cardinality == 1:
      # value1 has a unique solution so we can create a single number from a
      # product of row [var1, var2, var3] * column [pos1, pos2, pos3].
      return Numberjack.Sum(variables, values)
    else:
      # Because duplicate, independent solutions are possible we must return
      # all possible variables independently. The user will need to carefully
      # qualify how some or all of these values are constrained.
      return _predicates.Predicates([
        variable * value for variable, value in zip(variables, values)
      ])

  def get_solutions(self):
    column_headers = list(self._dimension_factory.dimensions().keys())
    cells = []
    dimensions = list(self._dimension_factory.dimensions().items())
    first_header, first_values = dimensions[0]
    for first_value in first_values:
      row = [[first_value]]
      cells.append(row)
      for column_header, column_values in dimensions[1:]:
        true_values = []
        row.append(true_values)
        for column_value in column_values:
          variable = self.get_variables({
            first_header: first_value,
            column_header: column_value,
          })
          if variable.value() == 1:
            true_values.append(column_value)
    return column_headers, cells

  def dimension_constraints(self):
    return (
      self._dimensional_cardinality_constraints(),
      self._dimensional_inference_constraints(),
    )

  def _dimensional_cardinality_constraints(self):
    result = []
    for group, cardinality in self._dimension_factory.cardinality_groups():
      num_zeros = len(group) - 1
      if num_zeros == 0:
        continue
      elif num_zeros == 1:
        # This implies the group is size 2 and behaves like a boolean.
        a, b = group
        result.append(self.get_variables(a) != self.get_variables(b))
      else:
        variables = []
        for constraint in group:
          variable = self.get_variables(constraint)
          assert len(variable) == 1, 'Enforcing cardinality impossible for %s' % (
            constraint
          )
          variables.append(variable[0])
        if cardinality:
          # Expect to find `cardinality` matches for `variables`.
          result.append(Numberjack.Sum(variables) == cardinality)
        else:
          # This signifies group is a set of unique scalar Variables.
          result.append(Numberjack.AllDiff(variables))
    return _predicates.Predicates(result)

  def _dimensional_inference_constraints(self):
    result = []
    for group in self._dimension_factory.inference_groups():
      variables = []
      group_cardinality = [slice_cardinality for _, slice_cardinality in group]
      if group_cardinality == [1, 1, 1]:
        # This is a simple case where every value being inferred has exactly one
        # solution.
        for constraint, slice_cardinality in group:
          variable = self.get_variables(constraint)
          assert len(variable) == 1, 'Enforcing cardinality impossible for %s' % (
            constraint
          )
          variables.append(variable[0])
        result.append(Numberjack.Sum(variables) != 2)
      elif list(sorted(group_cardinality))[0] == 1:
        # This is the only other supported configuration. If at least one slice
        # in the group has a fixed solution then that solution implies the other
        # solution at the other two slices are equal to each other.
        # Move the fixed group to the front.
        fixed, free_1, free_2 = map(
            lambda i: self.get_variables(i[0]),
            sorted(group, key=lambda i: i[1])
        )
        # This is equivalent to "if fixed then free_1 == free_2":
        result.append(fixed <= (free_1 == free_2))
    return _predicates.Predicates(result)

import ast
import itertools

import Numberjack

from data.logic import _dimension_factory, _expr_transformer, _predicates, \
  _reference, _solver, _util

_BASE_CONSTRAINTS = {
  _dimension_factory.Cardinality,
  _dimension_factory.TotalCardinality,
  _dimension_factory.UniqueCardinality,
  _dimension_factory.CardinalityRange,
}
_INFERENCE_CONSTRAINTS = {
  _dimension_factory.Inference,
  _dimension_factory.ValueSumsInference,
}
_DEFAULT_CONSTRAINTS = _BASE_CONSTRAINTS | _INFERENCE_CONSTRAINTS


class _Model(Numberjack.Model):
  Cardinality = _dimension_factory.Cardinality
  TotalCardinality = _dimension_factory.TotalCardinality
  UniqueCardinality = _dimension_factory.UniqueCardinality
  CardinalityRange = _dimension_factory.CardinalityRange

  Inference = _dimension_factory.Inference
  ValueSumsInference = _dimension_factory.ValueSumsInference

  def __init__(self, dimension_factory):
    super(_Model, self).__init__()
    self._dimension_factory = dimension_factory
    self._expr_transformer = _expr_transformer.ExprTransformer(self)
    self._variable_cache = {}
    self._constraints = []
    self._default_constraint_types = _DEFAULT_CONSTRAINTS.copy()
    self._preferred_solver = []
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
    self.add(self.dimension_constraints(
        types=tuple(self._default_constraint_types)))
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
          # Create a variable for address.
          upper_bound = min(
              self._dimension_factory.value_cardinality(value1),
              self._dimension_factory.value_cardinality(value2),
          )
          self._variable_cache[address] = Numberjack.Variable(
              0, upper_bound, address)
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
    """Returns table headers and rows."""
    dimensions = list(self._dimension_factory.dimensions().items())
    if dimensions:
      return self._get_dimension_values(dimensions)
    return self._get_model_values()

  def _get_dimension_values(self, dimensions):
    column_headers = list(self._dimension_factory.dimensions().keys())
    rows = []
    first_header, first_values = dimensions[0]
    for first_value in first_values:
      row = [[first_value]]
      rows.append(row)
      for column_header, column_values in dimensions[1:]:
        true_values = []
        row.append(true_values)
        compact, swap = self._dimension_factory.compact_dimensions(
            first_header, column_header)
        for column_value in column_values:
          variable = self.get_variables({
            first_header: first_value,
            column_header: column_value,
          })
          value = variable.value()
          if value == 1:
            true_values.append(column_value)
          elif compact and value:
            # MiniSat has strange, non-deterministic behavior for compacted
            # dimensions.
            if swap:
              variable = self.get_variables({
                first_header: None,
                column_header: column_value,
              })
            else:
              variable = self.get_variables({
                first_header: first_value,
                column_header: None,
              })
            # ...MiniSat also seems to function only in debugger mode which will
            # repr and str values...
            repr(variable), str(variable)
            if variable.value() == column_value:
              true_values.append(column_value)
              # ...and even still it can return 'true' multiple times.
          elif value:
            # `value` was chosen multiple times.
            true_values.append('%s*%s' % (column_value, value))
    return column_headers, rows

  def _get_model_values(self):
    column_headers = ['variables', 'values']
    rows = []
    for variable in sorted(self.variables, key=lambda v: v.operator):
      # ...MiniSat also seems to function only in debugger mode which will
      # repr and str values...
      repr(variable), str(variable)
      # `operator` matches the variable's given name.
      value = _util.numberjack_solution(variable)
      rows.append([[variable.operator], [value]])
    return column_headers, rows

  def disable_constraints(self, type=None):
    """Convenience method to omit default constraints in logic problem DSL."""
    if type is None:
      self._default_constraint_types -= _BASE_CONSTRAINTS
    else:
      self._default_constraint_types.remove(type)
    return lambda: print('Default constraints disabled')

  def disable_inference(self, type=None):
    """Convenience method to omit default inference in logic problem DSL."""
    if type is None:
      self._default_constraint_types -= _INFERENCE_CONSTRAINTS
    else:
      self._default_constraint_types.remove(type)
    return lambda: print('Default inference disabled')

  def solve_with(self, *solvers):
    self._preferred_solver = list(solvers)
    return lambda: print('Solving with: %s' % str(solvers))

  def get_solver(self):
    return self._preferred_solver

  def grid(self):
    """Convenience method for printing grid from within logic problem DSL."""
    return lambda: print('\n', self.get_solutions_grid())

  def get_solutions_grid(self):
    """Returns a large, traditional logic puzzle grid in tab-separated str.

    Intended to be used with spreadsheet software.
    """
    # Result with multiple dimensions is organized like so:
    # Columns: 0, n, n-1, n-2, ... 2
    # Rows: 1, 2, 3, ..., n
    dimensions = list(self._dimension_factory.dimensions().items())
    rows = []
    headers = ['*']
    for y_group in range(1, len(dimensions)):
      _, y_values = dimensions[y_group]
      for y_value in y_values:
        headers.append(str(y_value))
      headers.append('')
    rows.append('\t'.join(headers))
    for x_group in [0] + list(range(len(dimensions) - 1, 1, -1)):
      x_value_key, x_values = dimensions[x_group]
      for x_value in x_values:
        row = [str(x_value)]
        for y_group in range(1, len(dimensions)):
          y_value_key, y_values = dimensions[y_group]
          if x_value_key == y_value_key:
            break
          for y_value in y_values:
            variable = self.get_variables({
              x_value_key: x_value,
              y_value_key: y_value,
            })
            row.append(str(variable.value()))
          row.append('')  # Spacer between groups.
        rows.append('\t'.join(row))
      rows.append('')  # Spacer between groups.
    return '\n'.join(rows)

  def dimension_constraints(self, types=None):
    result = []
    for group in self._dimension_factory.dimension_constraint_groups():
      if types is not None and not isinstance(group, types):
        continue
      if hasattr(group, 'group'):
        variables = self._resolve_variables(group.group)
      else:
        variables = None
      if isinstance(group, _dimension_factory.UniqueCardinality):
        # This signifies group is a set of unique scalar Variables.
        result.append(Numberjack.AllDiff(variables))
      elif isinstance(group, _dimension_factory.Cardinality):
        cardinality = group.cardinality
        if len(variables) == 2 and cardinality == 1:
          # This implies the group is size 2 and behaves like a boolean.
          a, b = variables
          result.append(a != b)
        else:
          # Expect to find `cardinality` matches for `variables`.
          result.append(Numberjack.Sum(variables) == cardinality)
      elif isinstance(group, _dimension_factory.TotalCardinality):
        result.append(Numberjack.Sum(variables) == group.total)
      elif isinstance(group, _dimension_factory.CardinalityRange):
        s = Numberjack.Sum(variables)
        result.append(s >= group.min_cardinality)
        result.append(s <= group.max_cardinality)
      elif isinstance(group, _dimension_factory.Inference):
        if group.cardinalities == [1, 1, 1]:
          # This is a simple case where every value being inferred has exactly one
          # solution.
          result.append(Numberjack.Sum(variables) != 2)
        elif group.cardinalities[0] == 1:
          # This is the only other supported configuration. If at least one slice
          # in the group has a fixed solution then that solution implies the other
          # solution at the other two slices are equal to each other.
          # Move the fixed group to the front.
          fixed, free_1, free_2 = variables
          # This is equivalent to "if fixed then free_1 == free_2":
          result.append(fixed <= (free_1 == free_2))
      elif isinstance(group, _dimension_factory.ValueSumsInference):
        group_variables = map(self._resolve_variables, group.groups)
        group_sums = map(Numberjack.Sum, group_variables)
        constraints = sorted(
            zip(group_sums, group.scores), key=lambda x: x[1])
        reference, best_score = constraints.pop()
        for other, score in constraints:
          if best_score == 2 and score == 2:
            # If both scores are 2 then there is no need for inference.
            continue
          result.append(reference == other)
      else:
        raise NotImplementedError(
            '%s dimension constraint unsupported' % str(group))
    return _predicates.Predicates(result)

  def _resolve_variables(self, group):
    variables = []
    for constraint in group:
      variable = self.get_variables(constraint)
      assert len(variable) == 1, 'Enforcing cardinality impossible for %s' % (
        constraint
      )
      variables.append(variable[0])
    return variables

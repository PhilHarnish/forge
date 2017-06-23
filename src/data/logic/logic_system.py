import collections
import itertools

import Numberjack

from data.logic import _dimensions


class LogicSystem(object):
  def __init__(self, dimensions):
    self._input = dimensions
    self._dimensions = _dimensions._Dimensions(dimensions)
    self._model = Numberjack.Model()
    self._solver = None

  def _solve(self):
    if self._solver:
      return
    self._model.add(self._dimensions.constraints())
    self._solver = self._model.load('Mistral')
    self._solver.solve()

  def solution(self):
    self._solve()
    result = []
    for dimension in self._dimensions:
      result.append((dimension.name(), dimension.get_value()))
    return collections.OrderedDict(result)

  def __str__(self):
    """Produce useful, readable output."""
    self._solve()
    result = []
    for dimension_x, dimension_y in itertools.combinations(self._input, 2):
      x_values = self._input[dimension_x]
      y_values = self._input[dimension_y]
      for offset, x in enumerate(x_values):
        result.append('| ' * offset + str(x))
      for y in y_values:  # Rows.
        row = []
        for x in x_values:  # Columns
          if self._dimensions[x][y].get_value():
            row.append('#')
          else:
            row.append(' ')
        row.append(str(y))
        result.append(' '.join(row))
    return '\n'.join(result)

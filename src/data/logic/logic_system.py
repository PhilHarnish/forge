import collections

import Numberjack

from data.logic import _dimensions


class LogicSystem(object):
  def __init__(self, dimensions):
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

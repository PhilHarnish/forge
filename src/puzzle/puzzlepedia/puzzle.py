from typing import List, Type, Union

import numpy as np
from rx import subjects

from data import meta, observable_meta
from puzzle.heuristics import analyze
from puzzle.problems import problem
from puzzle.puzzlepedia import solution_stream

PuzzleTypes = Union['Puzzle', problem.ProblemData]


class Puzzle(subjects.Subject):
  _meta_problems: List['_MetaProblem']
  _child_streams: List[solution_stream.SolutionStream]

  def __init__(
      self, name: str, source: PuzzleTypes, hint: str = None, **kwargs) -> None:
    super(Puzzle, self).__init__()
    self._meta_problems = []
    self._child_streams = []
    if isinstance(source, str):
      data = [line for line in source.split('\n') if line]
    elif isinstance(source, list):
      data = source
    elif isinstance(source, Puzzle):
      data = source.solutions()
    elif isinstance(source, np.ndarray):
      data = source
    else:
      raise NotImplementedError(
          'Puzzle source type %s unsupported' % type(source))
    for i, (meta_problem, consumed) in enumerate(
        analyze.identify_problems(data, hint=hint)):
      p = _reify(meta_problem, '#%s' % i, consumed, **kwargs)
      self._meta_problems.append(p)
      self._child_streams.append(solution_stream.SolutionStream(str(i), p))
    self._observable = solution_stream.SolutionStream(
        name, observable_meta.ObservableMeta(), self._child_streams)
    self._observable.subscribe(self)

  def problem(self, index: int) -> '_MetaProblem':
    return self._meta_problems[index]

  def problems(self) -> List['problem.Problem']:
    return [p.active for p in self._meta_problems]

  def solutions(self) -> List[str]:
    return [p.solution for p in self._meta_problems]

  def get_next_stage(self) -> 'Puzzle':
    return Puzzle('meta', self)


def _reify(
    meta_problem: meta.Meta[Type[problem.Problem]],
    name: str,
    lines: problem.ProblemData,
    **kwargs,
) -> '_MetaProblem':
  result = _MetaProblem()
  for value, weight in meta_problem.items():
    result[value(name, lines, **kwargs)] = weight
  return result


class _MetaProblem(observable_meta.ObservableMeta):
  # Sentinel value for 'no solution found'.
  _NO_SOLUTION = object()

  def __init__(self) -> None:
    super(_MetaProblem, self).__init__()
    self._active = None
    self._solution = self._NO_SOLUTION

  @property
  def active(self) -> problem.Problem:
    return self._active or self.peek()

  @property
  def solution(self) -> str:
    if self._solution is self._NO_SOLUTION:
      self._solution = self.active.solutions().peek()
    return self._solution

  @solution.setter
  def solution(self, value: str):
    if self._solution == value:
      return
    self._solution = value
    self._changed()

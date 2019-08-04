from typing import List, Type, Union

import numpy as np
from rx import subjects

from data import meta, observable_meta
from puzzle.heuristics import analyze
from puzzle.problems import problem
from puzzle.puzzlepedia import meta_problem, solution_stream

PuzzleSources = Union['Puzzle', str, problem.ProblemData]


class Puzzle(subjects.Subject):
  _meta_problems: List[meta_problem.MetaProblem]
  _child_streams: List[solution_stream.SolutionStream]

  def __init__(
      self, name: str,
      source: PuzzleSources,
      hint: str = None,
      **kwargs) -> None:
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
    for i, (mp, consumed) in enumerate(
        analyze.identify_problems(data, hint=hint)):
      p = _reify(mp, '#%s' % (i + 1), consumed, **kwargs)
      self._meta_problems.append(p)
      self._child_streams.append(solution_stream.SolutionStream(str(i), p))
    self._observable = solution_stream.SolutionStream(
        name, observable_meta.ObservableMeta(), self._child_streams)
    self._observable.subscribe(self)

  def problem(self, index: int) -> meta_problem.MetaProblem:
    return self._meta_problems[index]

  def problems(self) -> List['problem.Problem']:
    return [p.active for p in self._meta_problems]

  def solutions(self) -> List[str]:
    return [p.solution for p in self._meta_problems]

  def get_next_stage(self) -> 'Puzzle':
    return Puzzle('meta', self)


def _reify(
    mp: meta.Meta[Type[problem.Problem]],
    name: str,
    lines: problem.ProblemData,
    **kwargs,
) -> meta_problem.MetaProblem:
  result = meta_problem.MetaProblem()
  for value, weight in mp.items():
    result[value(name, lines, **kwargs)] = weight
  return result

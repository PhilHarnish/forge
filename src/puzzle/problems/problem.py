"""
A `Problem` is one piece of a puzzle.

There are many kinds of problems:
* Crosswords (including cryptic)
* Encodings (morse, braille, numbers, ...)
* Images (encodings like semaphore, logic puzzles, ...)

A problem may be composed of Steps which may have individual Constraints.
Constraints may be used to configure the problem (such as specifying which
dictionaries to consult) or as knobs (such as min/max values for image
thresholds). These changes may influence future steps and, ultimately,
possible solutions.
"""

import collections
from typing import Collection, List, Union

import numpy as np

from data import meta
from puzzle.constraints import solution_constraints
from puzzle.steps import generate_solutions

_THRESHOLD = 0.01
ProblemData = Collection[Union[str, np.integer]]


class Problem(object):
  def __init__(
      self, name: str, lines: ProblemData, threshold: float=_THRESHOLD) -> None:
    self.name = name
    self.lines = lines
    self._solution_constraints = solution_constraints.SolutionConstraints()
    self._solution_constraints.weight_threshold = threshold
    self._solutions_generator = generate_solutions.GenerateSolutions(
        self._solution_constraints, self._solve_iter)
    self._notes = collections.defaultdict(list)

  @property
  def kind(self) -> str:
    return self.__class__.__name__

  @property
  def solution(self) -> str:
    return self._solutions_generator.solution

  def solutions(self) -> meta.Meta:
    return self._solutions_generator.solutions()

  def notes_for(self, solution) -> List[str]:
    return self._notes.get(solution, [])

  def __iter__(self) -> generate_solutions.Solutions:
    yield from self._solutions_generator

  def __str__(self) -> str:
    return '\n'.join(self.lines)

  def __repr__(self) -> str:
    return '%s(%s, %s)' % (
      self.__class__.__name__, repr(self.name), repr(self.lines))

  def _solve_iter(self) -> generate_solutions.Solutions:
    return iter(self._solve().items())

  def _solve(self) -> dict:
    """Solves Problem.

    Returns:
      dict Dict mapping solution to score.
    """
    raise NotImplementedError(
        '%s must implement _solve or _solve_iter' % self.__class__.__name__)

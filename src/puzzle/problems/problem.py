import collections
import itertools
from typing import Callable, Iterable, List, Tuple

from data import meta

_THRESHOLD = 0.01
Solution = Tuple[str, float]
Solutions = Iterable[Solution]


class Problem(object):
  def __init__(
      self, name: str, lines: List[str], threshold: float=_THRESHOLD) -> None:
    self.name = name
    self.lines = lines
    self._threshold = threshold or _THRESHOLD
    self._solutions_iterator = self._take_solutions_iter()
    self._all_solutions = meta.Meta()
    self._filtered_solutions_iterator = self._filter_solutions_iter()
    self._filtered_solutions = meta.Meta()
    self._notes = collections.defaultdict(list)
    self._constraints = [
      lambda k, v: v >= self._threshold
    ]

  @property
  def kind(self) -> str:
    return str(type(self)).strip("'<>").split('.').pop()

  @property
  def solution(self) -> str:
    if self._filtered_solutions.magnitude() >= 1:
      # At least one satisfactory answer already found.
      return self._filtered_solutions.peek()
    # Try to find just 1 good answer.
    self._filter_solutions_until(min_score=1)
    # Solutions will either be exhausted or include at least one with 1+ score.
    return self._filtered_solutions.peek()

  def constrain(self, fn: Callable[[str, float], bool]) -> None:
    self._constraints.append(fn)
    # Invalidate solutions.
    self._filtered_solutions_iterator = self._filter_solutions_iter()
    self._filtered_solutions = meta.Meta()

  def solutions(self) -> meta.Meta:
    for _ in self._filtered_solutions_iterator:
      # Exhaust the _filtered_solutions_iterator.
      pass
    return self._filtered_solutions

  def __iter__(self) -> Solutions:
    yield from self._filtered_solutions_iterator

  def notes_for(self, solution) -> List[str]:
    return self._notes.get(solution, [])

  def _solve_iter(self) -> Solutions:
    return iter(self._solve().items())

  def _take_solutions_iter(self) -> Solution:
    for k, v in self._solve_iter():
      self._all_solutions[k] = v
      yield k, v

  def _filter_solutions_iter(self) -> Solutions:
    # First review any existing values in _all_solutions. This is empty unless
    # the Problem's constraints changed mid-solve.
    for k, v in itertools.chain(
        self._all_solutions.items(), self._solutions_iterator):
      constrained = all(fn(k, v) for fn in self._constraints)
      if constrained:
        self._filtered_solutions[k] = v
        yield k, v

  def _filter_solutions_until(self, min_score: float=float('inf')) -> None:
    for k, v in self._filtered_solutions_iterator:
      if v >= min_score:
        break

  def _solve(self) -> dict:
    """Solves Problem.

    Returns:
      dict Dict mapping solution to score.
    """
    return self._all_solutions

  def __repr__(self) -> str:
    return '%s()' % self.__class__.__name__

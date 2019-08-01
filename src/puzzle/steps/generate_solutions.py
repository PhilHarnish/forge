import itertools
from typing import Any, Callable, Iterable, Tuple, Union

from data import meta
from puzzle.constraints import solution_constraints
from puzzle.steps import step

Solution = Tuple[str, float]
Solutions = Iterable[Union[Solution, StopIteration]]


class GenerateSolutions(step.Step):
  _solution_constraints: solution_constraints.SolutionConstraints

  def __init__(
      self,
      constraints: solution_constraints.SolutionConstraints,
      source: Callable[[], Solutions]) -> None:
    super(GenerateSolutions, self).__init__(constraints=(constraints,))
    self._solution_constraints = constraints
    self._solution_constraints.subscribe(self._on_constraints_changed)
    self._source = source
    # _all_solutions_iter() must only be called once.
    self._all_solutions_iterator = self._all_solutions_iter()
    self._all_solutions = meta.Meta()
    # _filter_solutions_iter() resets whenever constraints change.
    self._filtered_solutions_iterator = self._filter_solutions_iter()
    self._filtered_solutions = meta.Meta()

  def is_solution_valid(self, key: str, weight: float) -> bool:
    return self._solution_constraints.is_solution_valid(key, weight)

  @property
  def solution(self) -> str:
    if self._filtered_solutions.magnitude() >= 1:
      # At least one satisfactory answer already found.
      return self._filtered_solutions.peek()
    # Try to find just 1 answer with 1+ weight.
    for _, v in self._filtered_solutions_iterator:
      if v >= 1:
        break
    # Solutions will either be exhausted or include at least one with 1+ score.
    return self._filtered_solutions.peek()

  def solutions(self) -> meta.Meta:
    for _ in self._filtered_solutions_iterator:
      # Exhaust the _filtered_solutions_iterator.
      pass
    return self._filtered_solutions

  def __iter__(self) -> Solutions:
    yield from self._filtered_solutions_iterator

  def _on_constraints_changed(self, change: Any) -> None:
    del change
    # Invalidate filtered solutions.
    self._filtered_solutions_iterator = self._filter_solutions_iter()
    self._filtered_solutions = meta.Meta()

  def _all_solutions_iter(self) -> Solution:
    for next_value in self._source():
      if not isinstance(next_value, StopIteration):
        k, v = next_value
        self._all_solutions[k] = v
      yield next_value

  def _filter_solutions_iter(self) -> Solutions:
    # First review any existing values in _all_solutions. This is empty unless
    # the Problem's constraints changed mid-solve.
    for next_value in itertools.chain(
        self._all_solutions.items(), self._all_solutions_iterator):
      if isinstance(next_value, StopIteration):
        # We shouldn't expect any further values to survive filtering.
        # Stop iteration for now; iteration may restart again in future with
        # different constraints.
        return
      k, v = next_value
      if self.is_solution_valid(k, v):
        self._filtered_solutions[k] = v
        yield k, v

from typing import Optional, Union

from data import observable_meta
from puzzle.problems import problem

_NO_SOLUTION = object()


class MetaProblem(
    observable_meta.ObservableMeta[problem.Problem]):
  _solution: Union[object, str] = _NO_SOLUTION

  @property
  def active(self) -> problem.Problem:
    return self.peek()

  @property
  def solution(self) -> Optional[str]:
    if self._solution is _NO_SOLUTION:
      self._solution = self.active.solutions().peek()
    if self._solution is _NO_SOLUTION:
      return None
    return self._solution

  @solution.setter
  def solution(self, value: str):
    if self._solution == value:
      return
    self._solution = value
    self._changed()

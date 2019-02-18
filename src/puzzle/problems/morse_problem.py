import collections
from typing import ItemsView, Iterable, List

from puzzle.problems import problem

_ALPHABET = '.- /'  # " " = letter separator, "/" = word separator.


class MorseProblem(problem.Problem):
  def __init__(self, name: str, lines: List[str], **kwargs) -> None:
    super(MorseProblem, self).__init__(name, lines, **kwargs)
    self._frequencies = collections.Counter()
    for line in lines:
      self._frequencies.update(line)

  @staticmethod
  def score(lines: List[str]) -> float:
    return _score(lines)

  def _solve_iter(self) -> Iterable[ItemsView[str, float]]:
    yield 'asdf', 1


def _score(lines: List[str]) -> float:
  counts = collections.Counter()
  size = 0
  for line in lines:
    counts.update(line)
    size += len(line)
    if len(counts) > len(_ALPHABET):
      return 0
  if len(counts) <= 1:
    return 0  # Minimal input.
  # There are [1, _ALPHABET] symbols.
  if all(c in _ALPHABET for c in counts):
    return 1  # Looks like ordinary morse.
  elif '.' in counts and '-' in counts:
    margin_of_error = .1
  else:
    margin_of_error = 1
  # Increase confidence asymptotically with the size of input. Long inputs
  # with only 3 symbols are very morse-like.
  return (1 - margin_of_error) + (margin_of_error * (1 - 1 / size))

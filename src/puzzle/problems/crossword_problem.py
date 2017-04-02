import collections
import re

from src.data import crossword
from src.puzzle.problems import problem

_CROSSWORD_REGEX = re.compile(r'^.*\(([\d\s,|]+)\)$')
_INTS = re.compile(r'(\d+)')

class CrosswordProblem(problem.Problem):
  def __init__(self, name, lines):
    super(CrosswordProblem, self).__init__(name, lines)
    self._conn = None
    self._cursor = None
    for line in lines:
      for match in _CROSSWORD_REGEX.finditer(line):
        lengths = _INTS.findall(match.group(1))
        if len(lengths) == 1:
          self.constrain(lambda x, _: len(x) == int(lengths[0]))
        else:
          target = sum(map(int, lengths))
          self.constrain(lambda x, _: len(x) >= target)
        break

  @staticmethod
  def score(src):
    # TODO: Look for common crossword expressions.
    if _CROSSWORD_REGEX.match(src):
      return 1
    # Something with a lot of words *might* be a crossword clue.
    return max(0, 0.5 * (min(5, len(src.split())) / 5))

  def _get_cursor(self):
    if self._cursor is None:
      self._conn, self._cursor = crossword.connect('data/crossword.sqlite')
    return self._cursor

  def _solve(self):
    results = crossword.query(self._get_cursor(), ''.join(self.lines))
    ranked = []
    for (solution, frequency, keywords) in results:
      rank = self._rank(solution)
      if rank:
        ranked.append((solution, rank))
    return collections.OrderedDict(
        sorted(ranked, key=lambda x: x[1], reverse=True))

  def _rank(self, solution):
    return 1

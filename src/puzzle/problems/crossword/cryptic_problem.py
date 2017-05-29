from data.alphabets import cryptic_keywords
from puzzle.problems.crossword import _base_crossword_problem


class CrypticProblem(_base_crossword_problem._BaseCrosswordProblem):
  def __init__(self, name, lines):
    super(CrypticProblem, self).__init__(name, lines)
    self._tokens = lines[0].split()

  @staticmethod
  def score(lines):
    if len(lines) > 1:
      return 0
    line = lines[0]
    parts = line.split()
    if any(part in cryptic_keywords.ALL_INDICATORS for part in parts):
      return 1
    return _base_crossword_problem.score(lines) * .9  # Lower than normal.

  def _solve(self):
    return {}

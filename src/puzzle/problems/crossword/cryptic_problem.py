from data.alphabets import cryptic_keywords
from puzzle.problems.crossword import _base_crossword_problem


class CrypticProblem(_base_crossword_problem._BaseCrosswordProblem):
  @staticmethod
  def score(lines):
    if len(lines) > 1:
      return 0
    line = lines[0]
    parts = line.split()
    if any(part in cryptic_keywords.ALL_INDICATORS for part in parts):
      return 1
    # TODO: Look for common crossword expressions.
    return _base_crossword_problem.score(lines) * .9  # Lower than normal.

  def _solve(self):
    return {}

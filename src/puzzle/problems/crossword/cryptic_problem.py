from data.alphabets import cryptic_keywords
from puzzle.problems.crossword import _base_crossword_problem


class CrypticProblem(_base_crossword_problem._BaseCrosswordProblem):
  @staticmethod
  def score(lines):
    if len(lines) > 1:
      return 0
    line = lines[0]
    if any(indicator in line for indicator in cryptic_keywords.ALL_INDICATORS):
      return 1
    # TODO: Look for common crossword expressions.
    return _base_crossword_problem.score(lines) * .9  # Lower than normal.

  def _solve(self):
    raise NotImplementedError()

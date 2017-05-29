from puzzle.problems.crossword import _base_crossword_problem


class CrypticProblem(_base_crossword_problem._BaseCrosswordProblem):
  @staticmethod
  def score(lines):
    # TODO: Look for common crossword expressions.
    return _base_crossword_problem.score(lines) * .9  # Lower than normal.

  def _solve(self):
    raise NotImplementedError()

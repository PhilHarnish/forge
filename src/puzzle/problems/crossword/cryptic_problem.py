import re

from puzzle.problems import problem

_CROSSWORD_REGEX = re.compile(r'^.*\(([\d\s,|]+)\)$')
_INTS = re.compile(r'(\d+)')


class CrypticProblem(problem.Problem):
  @staticmethod
  def score(lines):
    # TODO: Look for common crossword expressions.
    return score_base(lines) * .9  # Lower than normal.

  def _solve(self):
    raise NotImplementedError()


def score_base(lines):
  if len(lines) > 1:
    return 0
  src = lines[0]
  # TODO: Look for common crossword expressions.
  if _CROSSWORD_REGEX.match(src):
    return 1
  # Something with a lot of words *might* be a crossword clue.
  return max(0.0, 0.5 * (min(5, len(src.split())) / 5))

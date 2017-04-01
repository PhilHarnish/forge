import re

from src.puzzle.problems import problem

_CROSSWORD_REGEX = re.compile(r'^.*\([\d\s,|]+\)$')

class CrosswordProblem(problem.Problem):
  @staticmethod
  def score(src):
    # TODO: Look for common crossword expressions.
    if _CROSSWORD_REGEX.match(src):
      return 1
    # Something with a lot of words *might* be a crossword clue.
    return max(0, 0.5 * (min(5, len(src.split())) / 5))

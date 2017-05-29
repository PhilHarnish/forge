from data import crossword
from data.alphabets import cryptic_keywords
from puzzle.problems.crossword import _base_crossword_problem


class CrypticProblem(_base_crossword_problem._BaseCrosswordProblem):
  def __init__(self, name, lines):
    super(CrypticProblem, self).__init__(name, lines)
    self._tokens = dict(enumerate(crossword.tokenize_clue(lines[0])))

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
    solutions = {}
    _visit(self._tokens, set(), solutions)
    return solutions


def _visit(tokens, visited, solutions):
  for i in range(0, len(tokens)):
    if i in visited:
      continue
    token = tokens[i]
    if token not in cryptic_keywords.ALL_INDICATORS:
      continue
    # TODO: Something interesting.
    visited.add(i)
    _visit(tokens, visited, solutions)
    visited.remove(i)

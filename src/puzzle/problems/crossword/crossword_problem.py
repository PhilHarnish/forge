import collections
import re

from data import crossword, warehouse
from puzzle.problems.crossword import _base_crossword_problem

_CROSSWORD_REGEX = re.compile(r'^.*\(([\d\s,|]+)\)$')
_INTS = re.compile(r'(\d+)')


class CrosswordProblem(_base_crossword_problem._BaseCrosswordProblem):
  @staticmethod
  def score(lines):
    return _base_crossword_problem.score(lines)

  def _solve(self):
    clue = ''.join(self.lines)
    clue_keywords = crossword.clue_keywords(clue)
    cursor = warehouse.get('/phrases/crossword/cursor')
    results = crossword.query(cursor, clue)
    if not results:
      return {}
    max_frequency = max([f for _, f, _ in results])
    ranked = []
    for (solution, frequency, keywords) in results:
      score = 0.0
      for keyword in clue_keywords:
        # Increase score by how often the keyword appeared in other clues.
        score += keywords[keyword] / frequency
      # Normalize score based on how many keywords were considered.
      score /= len(clue_keywords)
      rank = score * frequency / max_frequency
      if rank:
        ranked.append((solution, rank))
    return collections.OrderedDict(
        sorted(ranked, key=lambda x: x[1], reverse=True))

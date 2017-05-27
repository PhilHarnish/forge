import collections
import re

from data import crossword, warehouse
from puzzle.problems import problem

_CROSSWORD_REGEX = re.compile(r'^.*\(([\d\s,|]+)\)$')
_INTS = re.compile(r'(\d+)')

class CrosswordProblem(problem.Problem):
  def __init__(self, name, lines):
    super(CrosswordProblem, self).__init__(name, lines)
    for line in lines:
      for match in _CROSSWORD_REGEX.finditer(line):
        lengths = _INTS.findall(match.group(1))
        if len(lengths) == 1:
          self.constrain(lambda x, _: len(x) == int(lengths[0]))
        else:
          target = sum(map(int, lengths))
          if '|' in line:
            self.constrain(lambda x, _: len(x) >= target)
          else:
            self.constrain(lambda x, _: len(x) == target)
        break

  @staticmethod
  def score(lines):
    if len(lines) > 1:
      return 0
    src = lines[0]
    # TODO: Look for common crossword expressions.
    if _CROSSWORD_REGEX.match(src):
      return 1
    words = src.split()
    num_words = sum(word.isalpha() for word in words)
    if num_words < len(words) / 2:
      return 0
    # Something with a lot of words *might* be a crossword clue.
    return max(0.0, 0.5 * (min(5, num_words) / 5))

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

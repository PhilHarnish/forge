import collections

from data import warehouse
from puzzle.heuristics import analyze_word
from puzzle.problems import problem


class AnagramProblem(problem.Problem):

  @staticmethod
  def score(lines):
    # TODO: Support more input.
    if len(lines) > 1:
      return 0
    return analyze_word.score_anagram(lines[0])

  def _solve(self):
    index = warehouse.get('/words/unigram/anagram_index')
    results = collections.OrderedDict()
    if self.lines[0] not in index:
      return results
    for index, word in reversed(list(enumerate(index[self.lines[0]]))):
      # TODO: Use frequency for score.
      results[word] = index + 1
    return results

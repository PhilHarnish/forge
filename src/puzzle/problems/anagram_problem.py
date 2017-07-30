import collections

from data import warehouse
from puzzle.heuristics import analyze_word
from puzzle.problems import problem


class AnagramProblem(problem.Problem):

  @staticmethod
  def score(lines):
    if len(lines) > 1:
      return 0
    return analyze_word.score_anagram(lines[0])

  def _solve(self):
    index = warehouse.get('/words/unigram/anagram_index')
    if self.lines[0] not in index:
      return {}
    results = collections.OrderedDict()
    for index, word in enumerate(index[self.lines[0]]):
      results[word] = 1 / (index + 1)
    return results

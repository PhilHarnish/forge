from rx import Observable

from src.puzzle.heuristics import acrostic

class Acrostic(acrostic.BaseAcrostic):
  """Simple Acrostic solver.

  Lacks the ability to solve for multi-word solutions.
  """
  def __init__(self, words, trie):
    self._words = [set(word) for word in words]
    self._trie = trie
    self._source = Observable.from_(self)
    self.subscribe = self._source.subscribe
    self._cost = 0

  def __iter__(self):
    self._cost = 0
    for key, value in self._trie.walk(self._words):
      self._cost += 1
      yield key

  def cost(self):
    return self._cost

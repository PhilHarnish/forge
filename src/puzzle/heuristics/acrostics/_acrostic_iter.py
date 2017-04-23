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
    l = len(self._words)
    acc = [''] * l
    results = set()
    def _visit(words, i):
      next = i + 1
      if next >= l:  # End of list.
        for c in words[i]:
          acc[i] = c
          word = ''.join(acc)
          self._cost += 1
          if word in self._trie and word not in results:
            results.add(word)
            yield word
      else:
        for c in words[i]:
          acc[i] = c
          # Assume trie has words which start with every letter and so
          # i == 0 is never skipped. Otherwise, check prefixes.
          if i and not self._trie.items(''.join(acc[:next])):
            continue
          for result in _visit(words, next):
            yield result  # Up the trampoline.
    return _visit(self._words, 0)

  def cost(self):
    return self._cost

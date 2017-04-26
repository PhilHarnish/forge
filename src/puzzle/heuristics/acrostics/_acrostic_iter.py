import heapq

from rx import Observable

from data import meta
from puzzle.heuristics import acrostic

_EMPTY = (None, 0)
# Try to average 3 letters per word.
_TARGET_WORD_LEN = 4

class Acrostic(acrostic.BaseAcrostic):
  """Acrostic solver."""

  def __init__(self, words, trie):
    self._words = [set(word) for word in words]
    self._solution_len = len(words)
    self._trie = trie
    self._source = Observable.from_(self)
    self.subscribe = self._source.subscribe
    # Since we can assume there will be 1 letter phrases for every letter
    # go ahead and create n Meta objects to hold phrases from [n, m].
    self._phrase_graph = [
      {} for _ in range(0, self._solution_len)
    ]
    self._walks = [
      self._trie.walk(self._words[i:]) for i in range(0, self._solution_len)
    ]

  def __iter__(self):
    for phrase, weight in self._walk_phrase_graph_from(0, []):
      yield phrase

  def items(self):
    return iter(self._walk_phrase_graph_from(0, []))

  def _walk_phrase_graph_from(self, pos, acc):
    target = self._solution_len
    for phrase, weight in self._phrases_at(pos):
      phrase_len = len(phrase)
      acc.append(phrase)
      pos += phrase_len
      if pos < target:
        acc_len = len(acc)
        interesting = (
          (acc_len < 4) or (pos / acc_len >= _TARGET_WORD_LEN))
        if interesting:
          for result in self._walk_phrase_graph_from(pos, acc):
            # Forward any findings from recursive calls up the trampoline.
            yield result
      elif pos == target:
        yield ' '.join(acc), weight
      else:
        raise Exception('Desired length exceeded.')
      pos -= phrase_len
      acc.pop()

  def _phrases_at(self, pos):
    # phrases_at[0] has words of length 1, etc.
    phrases_at = self._phrase_graph[pos]
    # Exhaust known phrases first.
    for phrase in self._iter_phrases(phrases_at):
      yield phrase
    # Then find more.
    for phrase in self._walk(pos):
      yield phrase

  def _walk(self, pos):
    phrases_at = self._phrase_graph[pos]
    for phrase, weight in self._walks[pos]:
      length_l_phrases = phrases_at.setdefault(len(phrase), meta.Meta())
      length_l_phrases[phrase] = weight
      yield phrase, weight

  def _iter_phrases(self, phrases):
    # Exhaust known phrases first.
    best_phrases = []
    cache = []
    for pos, l in phrases.items():
      best_items = iter(l.items())
      next_best_tuple = next(best_items, _EMPTY)
      if next_best_tuple is not _EMPTY:
        item, weight = next_best_tuple
        # Cache the real data for this queue entry somewhere else.
        # cache[id] contains a tuple of (next_best_tuple, best_items)
        heapq.heappush(best_phrases, (1/weight, len(cache)))
        cache.append((next_best_tuple, best_items))
    while best_phrases:
      _, cache_id = best_phrases[0]
      next_best_tuple, best_items = cache[cache_id]
      yield next_best_tuple
      next_best_tuple = next(best_items, _EMPTY)
      if next_best_tuple is _EMPTY:
        heapq.heappop(best_phrases)
      else:
        item, weight = next_best_tuple
        cache[cache_id] = (next_best_tuple, best_items)
        heapq.heapreplace(best_phrases, (1/weight, cache_id))

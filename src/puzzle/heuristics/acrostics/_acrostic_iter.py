import heapq

from rx import Observable

from data import meta
from puzzle.heuristics import _base_acrostic

_EMPTY = (None, 0)
# Try to average 3 letters per word.
_TARGET_WORD_LEN = 3


class AcrosticIter(_base_acrostic.BaseAcrostic):
  """Acrostic solver.

  Iterative solver with depth-first behavior.
  """

  def __init__(self, words, trie=None):
    super(AcrosticIter, self).__init__(words, trie)
    self._solution_len = len(words)
    self._source = Observable.from_(self)
    self.subscribe = self._source.subscribe
    # Since we can assume there will be 1 letter phrases for every letter
    # go ahead and create n Meta objects to hold phrases from n->m at [n][m].
    self._phrase_graph = [
      {} for _ in range(0, self._solution_len)
    ]
    self._walks = []
    for i in range(0, self._solution_len):
      try:
        self._walks.append(self._trie.walk(self._words[i:]))
      except IndexError:
        break

  def __iter__(self):
    for phrase, weight in self._walk_phrase_graph_from(0, [], 0):
      yield phrase

  def items(self):
    for phrase, weight in self._walk_phrase_graph_from(0, [], 0):
      yield phrase, weight

  def _walk_phrase_graph_from(self, pos, acc, acc_weight):
    target = self._solution_len
    for phrase, weight in self._phrases_at(pos):
      yield from self._recurse_with(
          pos, acc, acc_weight, target, phrase, weight)

  def _recurse_with(self, pos, acc, acc_weight, target, phrase, weight):
    phrase_len = len(phrase)
    acc.append((phrase, weight))
    pos += phrase_len
    acc_weight += weight
    acc_len = len(acc)
    if pos < target:
      interesting = (acc_len < 3) or (pos / acc_len >= _TARGET_WORD_LEN)
      if interesting:
        for result in self._walk_phrase_graph_from(pos, acc, acc_weight):
          # Forward any findings from recursive calls up the trampoline.
          yield result
    elif pos == target:
      if len(acc) < target:  # Reject solutions composed of split letters.
        scored = _scored_solution(self._trie.interesting_threshold(), acc)
        yield scored
    else:
      raise Exception('Desired length exceeded.')
    pos -= phrase_len
    acc_weight -= weight
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
    if pos >= len(self._walks):
      return
    phrases_at = self._phrase_graph[pos]
    for phrase, weight in self._walks[pos]:
      l = len(phrase)
      if l not in phrases_at:
        phrases_at[l] = meta.Meta()
      length_l_phrases = phrases_at[l]
      length_l_phrases[phrase] = weight
      yield phrase, weight

  def _iter_phrases(self, phrases):
    """Uses a heap to yield from lists of `phrases` in sorted order.

    Sadly, this is 5% faster than the built-in heapq.merge solution:
      yield from heapq.merge(
          *[best_items.items() for pos, best_items in phrases.items()],
          key=lambda x: x[1], reverse=True)
    """
    if not phrases:
      return
    best_phrases = []
    cache = []
    for pos, l in phrases.items():
      best_items = iter(l.items())
      next_best_tuple = next(best_items, _EMPTY)
      if next_best_tuple is not _EMPTY:
        item, weight = next_best_tuple
        # Cache the real data for this queue entry somewhere else.
        # cache[id] contains a tuple of (next_best_tuple, best_items)
        heapq.heappush(best_phrases, (-weight, len(cache)))
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
        heapq.heapreplace(best_phrases, (-weight, cache_id))


def _scored_solution(target_score, acc):
  words = ' '.join(i[0] for i in acc)
  num_words = len(acc)
  avg_weight = sum(i[1] for i in acc) / len(acc)
  weighted_score = avg_weight / target_score
  result = (
    words,
    min(1 / num_words, weighted_score)
  )
  return result

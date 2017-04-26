import heapq

from rx import Observable

from data import meta
from puzzle.heuristics import acrostic

_EMPTY = (None, 0)
# Try to average 3 letters per word.
_TARGET_WORD_LEN = 4
# Target score per letter.
# Emperically determined from 1 sample:
#   (64649558 + 4705743816 + 46688059 + 495684) /
#   len(''.join('answer is flat expanse'.split())) = 253556690.36842105
_TARGET_WORD_SCORE_RATE = 200000000

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
    for phrase, weight in self._walk_phrase_graph_from(0, [], 0):
      yield phrase

  def items(self):
    return iter(self._walk_phrase_graph_from(0, [], 0))

  def _walk_dijkstra(self, phrase_graph, ignore_nodes, ignore_edges):
    fringe = _Queue()  # TODO: Inline.
    while fringe:
      fringe.pop()

  def _walk_phrase_graph_from(self, pos, acc, acc_weight):
    target = self._solution_len
    for phrase, weight in self._phrases_at(pos):
      phrase_len = len(phrase)
      acc.append(phrase)
      pos += phrase_len
      acc_weight += weight
      acc_len = len(acc)
      word_score_rate = float(acc_weight) / pos
      if pos < target:
        interesting = (acc_len < 3) or (pos / acc_len >= _TARGET_WORD_LEN)
        if interesting:
          for result in self._walk_phrase_graph_from(pos, acc, acc_weight):
            # Forward any findings from recursive calls up the trampoline.
            yield result
      elif pos == target:
        yield ' '.join(acc), acc_weight
      else:
        raise Exception('Desired length exceeded.')
      pos -= phrase_len
      acc_weight -= weight
      acc.pop()
      if word_score_rate < _TARGET_WORD_SCORE_RATE:
        # Interesting words for this position have been exhausted.
        break

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
      l = len(phrase)
      if l not in phrases_at:
        phrases_at[l] = meta.Meta()
      length_l_phrases = phrases_at[l]
      length_l_phrases[phrase] = weight
      yield phrase, weight

  def _iter_phrases(self, phrases):
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


class _Queue(object):
  def __init__(self):
    self._queue = []
    self._pool = []
    self._free_positions = []

  def __len__(self):
    return len(self._queue)

  def push(self, cost, o):
    if self._free_positions:
      idx = self._free_positions.pop()
      self._pool[idx] = o
    else:
      idx = len(self._pool)
      self._pool.append(o)
    heapq.heappush(self._queue, (cost, idx))

  def get_min(self):
    _, min_idx = self._queue[0]
    return self._pool[min_idx]

  def pop(self, index=None):
    _, idx = heapq.heappop(self._queue)
    result = self._pool[idx]
    self._pool[idx] = None
    self._free_positions.append(idx)
    return result

  def replace_min(self, cost, o):
    _, min_idx = self._queue[0]  # Peek at min for idx.
    self._pool[min_idx] = o  # Reuse that idx.
    heapq.heapreplace(self._queue, (cost, min_idx))

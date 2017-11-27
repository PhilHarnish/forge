from data import max_heap
from puzzle.heuristics.acrostics import _acrostic_iter

_EMPTY = (None, 0)
# Try to average 3 letters per word.
_TARGET_WORD_LEN = 4


class AcrosticSearch(_acrostic_iter.AcrosticIter):
  """Acrostic solver.

  Acrostic search using A* search.
  """
  def _walk_phrase_graph_from(self, pos, acc, acc_weight):
    # Goal:
    # - `target` length phrases score 1 * weight.
    # - 1 length phrases score (pos + 1)/target * weight.
    target = self._solution_len
    remaining_distance = target - pos
    interval_size = 1 / remaining_distance
    heap = max_heap.MaxHeap()
    for phrase, weight in self._phrases_at(pos, acc):
      phrase_len = len(phrase)
      normalized_weight = min(1, weight / self._trie.interesting_threshold())
      score = (phrase_len + normalized_weight) * interval_size
      heap.push(score, phrase)
      best_weight = heap.best_weight()
      while score < best_weight:
        # _phrases_at is yielding values which, even when scaled by 100% (i.e.
        # full length) can not exceed the best score we have in the heap.
        # Proceed from heap.
        best_phrase = heap.pop()
        yield from self._recurse_with(
            pos, acc, acc_weight, target, best_phrase, best_weight)
        best_weight = heap.best_weight()
    while len(heap):
      best_weight = heap.best_weight()
      best_phrase = heap.pop()
      yield from self._recurse_with(
          pos, acc, acc_weight, target, best_phrase, best_weight)

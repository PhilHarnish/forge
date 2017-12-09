from typing import Optional, Sequence, Tuple

from data.seek.node import Node

WeightedWord = Tuple[str, float]


class Trie2(dict):
  def __init__(self: 'Trie2', items: Sequence[WeightedWord]):
    super(Trie2, self).__init__()
    self._index = Node()
    self._length = 0
    self._smallest = float('inf')
    for key, value in items:
      self._add_to_index(key, value)

  def __contains__(self, key: str) -> bool:
    return _find_prefix(self._index, key) is not None

  def __len__(self) -> int:
    return self._length

  def __getitem__(self, key: str) -> float:
    return self._normalize_weight(_find_prefix(self._index, key).match_weight())

  def _normalize_weight(self, weight: float) -> float:
    # Normalize large weights to [0, 1].
    magnitude = self._index.magnitude()
    if magnitude > 1:
      return weight / magnitude
    return weight

  def _add_to_index(self, word: str, weight: float) -> None:
    if weight > self._smallest:
      raise AssertionError(
          'Items must be added to Trie2 in descending order.')
    else:
      self._smallest = weight
    self._index.add(word, weight)
    self._length += 1


def _find_prefix(cursor: Node, prefix: str) -> Optional[Node]:
  l = len(prefix)
  pos = 0
  while cursor and pos < l:
    target = prefix[pos]
    cursor = cursor.get(target)
    pos += 1
  return cursor

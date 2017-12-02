from data.trie2.node import Node


class Trie2(dict):
  def __init__(self, items):
    super(Trie2, self).__init__()
    self._index = Node()
    self._length = 0
    self._smallest = float('inf')
    for key, value in items:
      self._add_to_index(key, value)

  def __contains__(self, key):
    return self._find_prefix(key) is not None

  def __len__(self):
    return self._length

  def __getitem__(self, key):
    cursor = self._find_prefix(key)
    return self._weight(cursor)

  def _weight(self, cursor):
    # Normalize large weights to [0, 1].
    if self._index._max_weight > 1:
      return cursor._match_weight / self._index._max_weight
    return cursor._match_weight

  def walk(self, seek):
    raise NotImplementedError()

  def _find_prefix(self, prefix):
    l = len(prefix)
    pos = 0
    cursor = self._index
    while pos < l:
      target = prefix[pos]
      cursor = cursor.get(target)
      if not cursor:
        break
      pos += 1
    if pos == l:
      return cursor
    return None

  def _add_to_index(self, word, weight):
    if weight > self._smallest:
      raise AssertionError(
          'Items must be added to Trie2 in descending order.')
    else:
      self._smallest = weight
    self._index.add(word, weight)
    self._length += 1

import collections
import functools
import re

_REAL_TRIE = False


class Trie(collections.OrderedDict):
  def __init__(self, data):
    self._smallest = float('inf')
    # Trie's index (highest value characters first).
    self._index = []
    super(Trie, self).__init__(data)

  def __setitem__(self, key, value, *args, **kwargs):
    if value > self._smallest:
      raise AssertionError('Items must be added to trie in descending order.')
    else:
      self._smallest = value
    super(Trie, self).__setitem__(key, value, *args, **kwargs)
    # TODO: Prevent redundant adds?
    if _REAL_TRIE:
      self._add_to_index(key, value)

  def has_keys_with_prefix(self, prefix):
    if _REAL_TRIE:
      l = len(prefix)
      pos = 0
      cursor = self._index
      searching = True
      while searching and pos < l:
        searching = False
        target = prefix[pos]
        for dst_c, weight, children in cursor:
          if dst_c == target:
            searching = True
            pos += 1
            cursor = children
            break
      return pos == l
    else:
      return any([key.startswith(prefix) for key in self])

  def keys(self, prefix=''):
    if prefix:
      return [key for key in self if key.startswith(prefix)]
    return iter(self)

  def items(self, prefix=None, seek=None):
    result = super(Trie, self).items()
    if not seek:
      if prefix:
        return [kvp for kvp in result if kvp[0].startswith(prefix)]
      return result
    l = len(prefix)
    return [
      (key, weight) for key, weight in result if key.startswith(prefix) and (
          len(key) < l or key[l] in seek)
    ]

  def walk(self, seek_sets):
    """Returns solutions matching `seek_sets`, ordered from high to low."""
    # Convert seek_sets into a regular expression.
    matcher = _regexp(seek_sets)
    for key, value in self.items():
      if matcher.match(key):
        yield (key, value)

  def _add_to_index(self, word, weight):
    # TODO: This takes ~5 seconds to initialize with massive data.
    l = len(word)
    cursor = self._index
    pos = 0
    searching = True
    while searching and pos < l:
      searching = False
      target = word[pos]
      for dst_c, _, children in cursor:
        if dst_c == target:
          searching = True
          pos += 1
          cursor = children
          break
    for i in range(pos, len(word)):
      children = []
      cursor.append((word[i], weight, children))
      cursor = children


functools.lru_cache(maxsize=1)
def _regexp(seek_sets):
  return re.compile(''.join([
    '^',
    '[%s]' % ''.join(seek_sets[0]),
  ] + [
    '($|[%s])' % ''.join(s) for s in seek_sets[1:]
  ] + [
    '$'
  ]))

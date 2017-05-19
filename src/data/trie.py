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
      return self._find_prefix(prefix) is not None
    else:
      return any([key.startswith(prefix) for key in self])

  def _find_prefix(self, prefix):
    l = len(prefix)
    pos = 0
    cursor = self._index
    searching = True
    while searching and pos < l:
      searching = False
      target = prefix[pos]
      for row in cursor:
        if len(row) == 3:
          dst_c, _, _ = row
          children = None
        else:
          dst_c, _, _, *children = row
        if dst_c == target:
          pos += 1
          if children:
            searching = True
            cursor = children
          break
    if pos == l:
      return cursor
    return None

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
      for row in cursor:
        if len(row) == 2:
          dst_c, _, terminal = row
          children = None
        else:
          dst_c, _, terminal, *children = row
        if dst_c == target:
          pos += 1
          if pos == l:
            # Exhausted input; this spells something now.
            row[2] = True
            return
          elif children:
            # More children to consider.
            searching = True
            cursor = children
          else:
            # Exhausted trie. Add in-place.
            cursor = row
          break
    end = len(word) - 1
    for i in range(pos, len(word)):
      if i == end:
        cursor.append([word[i], weight, True])
      else:
        new_cursor = [word[i], weight, False]
        cursor.append(new_cursor)
        cursor = new_cursor


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

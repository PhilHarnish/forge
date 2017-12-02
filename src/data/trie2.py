

class _Node(object):
  __slots__ = (
    '_char_mask',
    '_length_mask',
    '_max_weight',
    '_match_weight',
    '_children',
  )

  def __init__(self):
    self._char_mask = 0
    self._length_mask = 0
    self._max_weight = 0
    self._match_weight = 0
    self._children = {}

  def get(self, k):
    return self._children.get(k, None)

  def add(self, k, v):
    l = len(k)
    pos = 0
    cursor = self
    char_masks = _char_masks(k)
    while pos < l:
      c = k[pos]
      cursor._char_mask |= char_masks[pos]
      cursor._length_mask |= 2 ** (l - pos)
      cursor._max_weight = max(cursor._max_weight, v)
      # Traverse to next.
      cursor_next = cursor.get(c)
      if not cursor_next:
        break
      cursor = cursor_next
      pos += 1
      has_children = bool(cursor._length_mask)
      if pos == l:
        if cursor._match_weight:
          # Duplicate addition.
          raise KeyError('%s already added' % k)
        # Exhausted input; this spells something new.
        cursor._match_weight = v
        return
      elif not has_children:
        break
    # Add remaining characters.
    while pos < l:
      c = k[pos]
      pos += 1
      cursor_next = _Node()
      cursor._children[c] = cursor_next
      cursor = cursor_next
      cursor._char_mask = char_masks[pos]
      cursor._length_mask = 2 ** (l - pos)
      cursor._max_weight = v
    cursor._match_weight = v

  def __repr__(self):
    chars = []
    for i in range(26):
      if self._char_mask & (2 ** i):
        chars.append(chr(ord('a') + i))
    if self._length_mask:
      # Convert mask to binary, reverse, and swap "01" for " #"
      lengths = bin(self._length_mask)[:1:-1].replace(
          '0', ' ').replace('1', '#')
    else:
      lengths = ''
    return '_Node(%s, %s, %s)' % (
      repr(''.join(chars)), repr(lengths), self._match_weight)

class Trie2(dict):
  def __init__(self, items):
    super(Trie2, self).__init__()
    self._index = _Node()
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

def _char_masks(s):
  result = [0]
  acc = 0
  for c in s[::-1]:
    if c < 'a' or c > 'z':
      raise IndexError('Trie2 cannot index %s' % c)
    acc |= 2 ** (ord(c) - 97)  # ord('a') == 97.
    result.append(acc)
  return list(reversed(result))

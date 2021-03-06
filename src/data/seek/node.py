from typing import Dict, ItemsView, List, Optional


class Node(object):
  __slots__ = (
    '_char_mask',
    '_length_mask',
    '_max_weight',
    '_match_weight',
    '_children',
  )

  _char_mask: int
  _length_mask: int
  _max_weight: int
  _match_weight: int
  _children: Dict[str, 'Node']

  def __init__(self: 'Node'):
    self._char_mask = 0
    self._length_mask = 0
    self._max_weight = 0
    self._match_weight = 0
    self._children = {}

  def children(self) -> Dict[str, 'Node']:
    return self._children

  def get(self, k: str) -> Optional['Node']:
    return self.children().get(k, None)

  def items(self) -> ItemsView[str, 'Node']:
    return self.children().items()

  def add(self, k: str, v: float):
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
      if cursor_next is None:
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
      cursor_next = Node()
      cursor._children[c] = cursor_next
      cursor = cursor_next
      cursor._char_mask = char_masks[pos]
      cursor._length_mask = 2 ** (l - pos)
      cursor._max_weight = v
    cursor._match_weight = v

  def match_weight(self) -> int:
    return self._match_weight

  def magnitude(self) -> int:
    return self._max_weight

  def shallow_copy(self) -> 'Node':
    n = Node()
    n._char_mask = self._char_mask
    n._length_mask = self._length_mask
    n._max_weight = self._max_weight
    n._match_weight = self._match_weight
    return n

  def set_flags(self, char_mask, length_mask, max_weight, match_weight) -> None:
    self._char_mask = char_mask
    self._length_mask = length_mask
    self._max_weight = max_weight
    self._match_weight = match_weight

  def __len__(self) -> int:
    return len(self.children())

  def __repr__(self) -> str:
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
    return '%s(%s, %s, %s)' % (
      self.__class__.__name__, repr(''.join(chars)), repr(lengths),
      self._match_weight)

def _char_masks(s: str) -> List[int]:
  result = [0]
  acc = 0
  for c in s[::-1]:
    if c < 'a' or c > 'z':
      raise IndexError('Trie2 cannot index %s' % c)
    acc |= 2 ** (ord(c) - 97)  # ord('a') == 97.
    result.append(acc)
  return list(reversed(result))

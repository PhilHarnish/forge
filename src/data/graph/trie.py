from typing import List

from data.graph import bloom_node


def add(cursor: bloom_node.BloomNode, k: str, v: float):
  l = len(k)
  pos = 0
  char_masks = _char_masks(k)
  while pos <= l:
    cursor.require(char_masks[pos])
    cursor.distance(l - pos)
    cursor.weight(v, pos == l)
    if pos < l:
      cursor = cursor.open(k[pos])
    pos += 1


def _char_masks(s: str) -> List[int]:
  result = [0]
  acc = 0
  for c in s[::-1]:
    if c < 'a' or c > 'z':
      raise IndexError('Node cannot mask %s' % c)
    acc |= 2 ** (ord(c) - 97)  # ord('a') == 97.
    result.append(acc)
  return list(reversed(result))

"""ngram graph producer.

Caches constructed tree for subsequent access (both in memory and on disk).
"""
from typing import Dict, List, Tuple

from data import data
from data.graph import bloom_mask


def index(src: str) -> Dict[str, List[Tuple[str, tuple]]]:
  """Open `src` and return a list of lists of lists of int.

  The leaves (char, int, tuple), nested recursively, and describe require_mask.
  These require_masks are wrapped as (masks, weight).
  Next, a List, ordered by length.
  Finally, a Dict keyed by initial character.
  """
  result = {c: [] for c in bloom_mask.BASE_ALPHABET}
  for line in data.open_project_path(src):
    words = line.split()
    word = words[0]
    initial = word[0]
    row = result[initial]
    length = len(word)
    missing = length - len(row)
    if missing > 0:
      row.extend([] for _ in range(missing))
    masks = _char_masks(word)
    weight = int(words.pop())
    row[length - 1].append((masks, weight))
  return result



_CHAR_MASK_CACHE = {
  c: (c, bloom_mask.for_alpha(c), None) for c in bloom_mask.ALPHABET
}


def _char_masks(s: str) -> tuple:
  if s in _CHAR_MASK_CACHE:
    return _CHAR_MASK_CACHE[s]
  # Find cached suffix.
  last_match = s[-1]
  for i in range(len(s) - 2, 0, -1):
    suffix = s[i:]
    if suffix in _CHAR_MASK_CACHE:
      last_match = suffix
    else:
      break
  result = _CHAR_MASK_CACHE[last_match]
  acc = result[1]
  suffix_length = len(last_match) + 1
  for c in s[-suffix_length::-1]:
    acc = bloom_mask.for_alpha(c) | acc
    result = (c, acc, result)
    _CHAR_MASK_CACHE[s[-suffix_length:]] = result
    suffix_length += 1
  return result

"""ngram graph producer.

Caches constructed tree for subsequent access (both in memory and on disk).
"""
import functools
from typing import Dict, List, Tuple

from data import data, pickle_cache, types
from data.graph import bloom_mask, bloom_node, trie

_FILES = [
  'data/g1m_1gram.txt',
] + ['data/coca_%sgram.txt' % i for i in range(2, 5+1)]


@functools.lru_cache(1)
@pickle_cache.cache('data/graph/ngram/graph')
def get(
    initial_mask: int = bloom_mask.REQUIRE_NOTHING,
    require_mask: int = bloom_mask.REQUIRE_NOTHING,
    lengths_mask: int = bloom_mask.ANY_LENGTHS) -> bloom_node.BloomNode:
  root = bloom_node.BloomNode()
  # TODO: Replace trie with in-place construction.
  trie.add_ngrams(root, _ngrams(initial_mask, require_mask, lengths_mask))
  return root


def matching(node: bloom_node.BloomNode) -> bloom_node.BloomNode:
  initial_mask = bloom_mask.REQUIRE_NOTHING
  for c in node.edges():
    initial_mask |= bloom_mask.for_alpha(c)
  return node * get(
      initial_mask=initial_mask,
      require_mask=node.require_mask,
      lengths_mask=node.lengths_mask)


def _ngrams(
    initial_mask, require_mask, lengths_mask) -> List[List[types.WeightedWord]]:
  # TODO: Profile and optimize.
  result = []
  for f in _FILES:
    results = []
    result.append(results)
    for initial, length_entries in index(f).items():
      initial_alpha = bloom_mask.for_alpha(initial)
      if not initial_alpha & initial_mask:
        continue
      length_entries_length = len(length_entries)
      if lengths_mask:
        length_mask_remaining = lengths_mask
      else:
        length_mask_remaining = (1 << length_entries_length) - 1
      pos = 0
      while pos < length_entries_length and length_mask_remaining:
        cursor = 1 << pos
        entries = length_entries[pos]
        pos += 1
        if not (cursor & length_mask_remaining):
          continue
        length_mask_remaining -= cursor  # Remove this bit from mask.
        for entry in entries:
          word, weight, masks = entry
          _, word_requires, _ = masks
          if require_mask and (require_mask & word_requires) != require_mask:
            continue  # Some of require_mask was missing from word.
          results.append((word, weight))
  return result


@pickle_cache.cache('data/graph/ngram/index')
def index(src: str) -> Dict[str, List[Tuple[str, str, tuple]]]:
  """Open `src` and return a list of lists of lists of int.

  The leaves (char, int, tuple), nested recursively, and describe require_mask.
  These require_masks are wrapped as (word, weight, masks).
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
    # TODO: Remove ' '.join(words).
    row[length - 1].append((' '.join(words), weight, masks))
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

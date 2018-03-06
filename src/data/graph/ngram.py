"""ngram graph producer.

Caches constructed tree for subsequent access (both in memory and on disk).
"""
import functools
from typing import Container, Dict, Iterable, List, Tuple

from data import data, pickle_cache
from data.graph import bloom_mask, bloom_node

_SPACE_MASK = bloom_mask.for_alpha(' ')
_NGRAM_ROOT = bloom_node.BloomNode()
_LOOPBACK_SCALE = 1/1024
_SCALED_ROOTS = {}
_FILES = [
  'data/g1m_1gram.txt',
] + ['data/coca_%sgram.txt' % i for i in range(2, 5+1)]


NgramLeaf = Tuple[str, int, tuple]
NgramEntry = Tuple[str, int, NgramLeaf]
ChildEntry = Tuple[int, int, NgramLeaf]


@functools.lru_cache(1)
@pickle_cache.cache('data/graph/ngram/graph')
def get(
    initial_mask: int = bloom_mask.REQUIRE_NOTHING,
    require_mask: int = bloom_mask.REQUIRE_NOTHING,
    lengths_mask: int = bloom_mask.ANY_LENGTHS) -> bloom_node.BloomNode:
  prefix = ''
  return _NGRAM_ROOT(
      prefix,
      _ngrams(prefix, initial_mask, require_mask, lengths_mask),
      merge=_merge_expand_initial)


def matching(node: bloom_node.BloomNode) -> bloom_node.BloomNode:
  initial_mask = bloom_mask.REQUIRE_NOTHING
  for c in node.edges():
    initial_mask |= bloom_mask.for_alpha(c)
  return node * get(
      initial_mask=initial_mask,
      require_mask=node.require_mask,
      lengths_mask=node.lengths_mask)


def _ngrams(
    prefix: str,
    initial_mask: int = bloom_mask.REQUIRE_NOTHING,
    require_mask: int = bloom_mask.REQUIRE_NOTHING,
    lengths_mask: int = bloom_mask.ANY_LENGTHS,
) -> List[NgramEntry]:
  results = []
  n_words = prefix.count(' ') + 1
  for word_count, f in enumerate(_FILES[:n_words], 1):
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
          if not prefix:
            pass
          elif not word.startswith(prefix):
            continue
          else:
            # Matching prefix.
            pass
          _, word_requires, _ = masks
          if require_mask and (require_mask & word_requires) != require_mask:
            continue  # Some of require_mask was missing from word.
          results.append(entry)
  return results


@pickle_cache.cache('data/graph/ngram/index')
def index(src: str) -> Dict[str, List[List[NgramEntry]]]:
  """Open `src` and return a list of lists of lists of int.

  The leaves (char, int, tuple), nested recursively, and describe require_mask.
  These leaf entries are wrapped as (words, weight, masks) in a List.
  Next, a List, ordered by length.
  Finally, a Dict keyed by initial character.
  """
  result = {c: [] for c in bloom_mask.BASE_ALPHABET}
  for line in data.open_project_path(src):
    parts = line.rpartition(' ')
    words = parts[0]
    word, _, _ = words.partition(' ')  # Discard other words.
    initial = word[0]
    row = result[initial]
    length = len(word)
    missing = length - len(row)
    if missing > 0:
      row.extend([] for _ in range(missing))
    masks = _char_masks(word)
    weight = int(parts[2])
    row[length - 1].append((words, weight, masks))
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


def _merge_expand_initial(
    host: bloom_node.BloomNode,
    sources: List[bloom_node.BloomNode],
    prefix: str,
    ngrams: Iterable[NgramEntry],
    whitelist: Container[str] = None,
    blacklist: Container[str] = None) -> None:
  assert not whitelist
  assert not blacklist
  assert not prefix
  _merge_expand_entries(
      host, sources, prefix, _unpack_initial_ngrams(ngrams),
      whitelist=whitelist,
      blacklist=blacklist)


def _merge_expand_entries(
    host: bloom_node.BloomNode,
    sources: List[bloom_node.BloomNode],
    prefix: str,
    ngrams: Iterable[ChildEntry],
    whitelist: Container[str] = None,
    blacklist: Container[str] = None) -> None:
  del sources
  assert not whitelist
  assert not blacklist
  children = []
  children_initial = None
  provide_mask = _SPACE_MASK
  require_mask = bloom_mask.REQUIRE_NOTHING
  lengths_mask = 0
  max_weight = 0
  match_weight = 0
  for child_length_mask, weight, masks in ngrams:
    initial, mask, child_mask = masks
    provide_mask |= mask
    require_mask &= mask
    lengths_mask |= child_length_mask
    if weight > max_weight:
      max_weight = weight
    if children_initial and initial != children_initial:
      _link_child(
          host, prefix + children_initial, children_initial, match_weight,
          children)
      children = []
      match_weight = 0
    if child_mask:
      children.append((child_length_mask >> 1, weight, child_mask))
    else:
      match_weight = weight
    children_initial = initial
  _link_child(
      host, prefix + children_initial, children_initial, match_weight, children)
  host.provide_mask = provide_mask
  host.require_mask = require_mask
  host.lengths_mask = lengths_mask
  host.max_weight = max_weight


def _link_child(
    host: bloom_node.BloomNode, prefix: str, initial: str, match_weight: int,
    ngrams: Iterable[ChildEntry]) -> None:
  if ngrams:
    child_node = _NGRAM_ROOT(prefix, ngrams, merge=_merge_expand_entries)
  elif match_weight:
    child_node = bloom_node.BloomNode()
    child_node.weight(match_weight, match=True)
    child_node.distance(0)
    root = _get_scaled_root(_LOOPBACK_SCALE)
    _cheap_link(child_node, ' ', root)
  else:
    raise TypeError('No children or match_weight for %s' % initial)
  _cheap_link(host, initial, child_node)


def _cheap_link(
    parent: bloom_node.BloomNode,
    initial: str,
    child: bloom_node.BloomNode) -> None:
  tmp_op = child.op
  child.op = None  # HACK: Avoid early expansion.
  parent.link(initial, child)
  child.op = tmp_op



def _unpack_initial_ngrams(
    ngrams: Iterable[NgramEntry]) -> Iterable[ChildEntry]:
  for word, weight, masks in ngrams:
    yield 1 << len(word), weight, masks


def _get_scaled_root(scale: float) -> bloom_node.BloomNode:
  if scale not in _SCALED_ROOTS:
    _SCALED_ROOTS[scale] = get() * scale
  return _SCALED_ROOTS[scale]

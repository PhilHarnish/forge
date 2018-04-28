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
  'data/g1m_sorted_1gram.txt',
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
  return _get(prefix, initial_mask, require_mask, lengths_mask)


def _get(
    prefix: str,
    initial_mask: int,
    require_mask: int,
    lengths_mask: int) -> bloom_node.BloomNode:
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
  if not prefix:
    n_words = 1
  else:
    n_words = prefix.count(' ') + 2
  ngram_index = index(_FILES[n_words - 1])
  key = hash(prefix)
  if key not in ngram_index:
    return results
  for entry in ngram_index[key]:
    word, weight, mask_tuples = entry
    _, masks, _ = mask_tuples
    if not masks & require_mask:
      continue
    word_initial_alpha = bloom_mask.for_alpha(word[0])
    if not word_initial_alpha & initial_mask:
      continue
    word_length_mask = 1 << len(word)
    if not word_length_mask & lengths_mask:
      continue
    results.append(entry)
  return results


@pickle_cache.cache('data/graph/ngram/index')
def index(src: str) -> Dict[int, List[List[NgramEntry]]]:
  """TODO: Docs."""
  result = {}
  for line in data.open_project_path(src):
    words, _, weight = line.rpartition('\t')
    prefix, _, word = words.rpartition(' ')
    masks = _char_masks(word)
    weight = int(weight)
    key = hash(prefix)
    if key not in result:
      result[key] = []
    result[key].append((word, weight, masks))
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
  children = []
  children_initial = None
  provide_mask = _SPACE_MASK
  require_mask = bloom_mask.REQUIRE_NOTHING
  lengths_mask = 0
  max_weight = 0
  child_provide_mask = _SPACE_MASK
  child_require_mask = bloom_mask.REQUIRE_NOTHING
  child_lengths_mask = 0
  child_max_weight = 0
  child_match_weight = 0
  for ngram_lengths_mask, weight, masks in ngrams:
    initial, mask, child_masks = masks
    # TODO: Why does a "pa" (use) breakpoint trigger here multiple times?
    # TODO: What is creating so many duplicate nodes?
    if whitelist and initial not in whitelist:
      continue
    elif blacklist and initial in blacklist:
      continue
    provide_mask |= mask
    require_mask &= mask
    lengths_mask |= ngram_lengths_mask
    if weight > max_weight:
      max_weight = weight
    if not children_initial:
      pass
    elif initial < children_initial:
      raise ValueError('Entries must be alphabetized')
    elif initial != children_initial:
      # Start a new group of children based on this initial.
      _link_child(
          host, prefix + children_initial, children_initial, child_provide_mask,
          child_require_mask, child_lengths_mask, child_max_weight,
          child_match_weight, children)
      children = []
      child_match_weight = 0
      child_provide_mask = _SPACE_MASK
      child_require_mask = bloom_mask.REQUIRE_NOTHING
      child_max_weight = 0
    if child_masks:
      if weight > child_max_weight:
        child_max_weight = weight
      _, child_mask, _ = child_masks
      child_provide_mask |= child_mask
      child_require_mask &= child_mask
      child_lengths_mask |= ngram_lengths_mask >> 1
      children.append((ngram_lengths_mask >> 1, weight, child_masks))
    else:
      child_match_weight = weight
    children_initial = initial
  if children_initial:
    _link_child(
        host, prefix + children_initial, children_initial, child_provide_mask,
        child_require_mask, child_lengths_mask, child_max_weight,
        child_match_weight, children)
  host.provide_mask = provide_mask
  host.require_mask = require_mask
  host.lengths_mask = lengths_mask
  host.max_weight = max_weight


def _link_child(
    host: bloom_node.BloomNode, prefix: str, initial: str, provide_mask: int,
    require_mask: int, lengths_mask:int, max_weight: int, match_weight: int,
    ngrams: Iterable[ChildEntry]) -> None:
  if not ngrams and not match_weight:
    raise TypeError('No children or match_weight for %s' % initial)
  if ngrams:
    child_node = _NGRAM_ROOT(prefix, ngrams, merge=_merge_expand_entries)
  else:
    child_node = bloom_node.BloomNode()
  child_node.provide_mask = provide_mask
  child_node.require_mask = require_mask
  child_node.lengths_mask = lengths_mask
  child_node.max_weight = max_weight
  if match_weight:
    child_node.weight(match_weight, match=True)
    child_node.distance(0)
    root = _get_scaled_root(_LOOPBACK_SCALE)
    # TODO: Find better requirements.
    ngrams = _get(
        prefix, bloom_mask.REQUIRE_NOTHING, bloom_mask.REQUIRE_NOTHING,
        bloom_mask.ANY_LENGTHS)
    _cheap_link(child_node, ' ', root + ngrams)
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

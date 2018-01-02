"""Produce BloomNode graphs from words.

TODO: Create a root Trie which lazy-expands based on sibling length_mask.
TODO: Is log(p1) + log(p2) better than p1*p2?
"""
from typing import List

from data import types
from data.graph import bloom_mask, bloom_node


def add(
    root: bloom_node.BloomNode, key: str, value: float) -> bloom_node.BloomNode:
  return _add(root, key, value, False)


def add_multi_word(
    root: bloom_node.BloomNode, key: str, value: float) -> bloom_node.BloomNode:
  l = len(key)
  pos = 0
  cursor = root
  whitespace_mask = bloom_mask.for_alpha(' ')
  while pos <= l:
    cursor.provide_mask |= whitespace_mask
    if pos < l:
      cursor = cursor.open(key[pos])
    pos += 1
  # This could be made more efficient if "value" was clamped and loop_back
  # nodes were shared.
  loop_back = root * value
  cursor.link(' ', loop_back)
  return cursor


def add_ngrams(
    root: bloom_node.BloomNode,
    ngrams: List[List[types.WeightedWord]],
    n_percentiles: int = 10) -> None:
  """Adds `ngrams` to `root`.

  Notes:
  The probability of a unigram match is:
    P(w_i) = c(w_i) / total_count
  The probability of a bigram match is:
    P(w_i | w_i - 1) = c(w_i - 1, w_i) / c(w_i - 1)
    Where:
      * c(w_i - 1, w_i) is the count of n-gram suffixes for (w_i - 1).
      * 1/c(w_i - 1) is the scale applied to all children of (w_i - 1).
      * 1/c(w_i) = 1/(total_count * P(w_i)) =
        1/(total_count * (c(w_i) / total_count)) = 1/(c(w_i))

  :param root: Starting point of trie.
  :param ngrams: Lists lists of (word, weight) tuples. First list is unigrams,
      second is bigrams, etc.
  :param n_percentiles: Number of percentiles to bucket loopback nodes to. Fewer
      buckets means more word->word subtrees can be reused.
  """
  ngram_map = {}
  for grams in ngrams:
    total_count = sum(weight for _, weight in grams)
    length = len(grams)
    percentile_size = length / n_percentiles
    min_scale = 0
    scale_percentile = -1
    for i, (ngram, count) in enumerate(grams):
      # Calculate statistics.
      percentile_group = i // percentile_size
      if percentile_group != scale_percentile:
        min_scale = count / total_count
        scale_percentile = percentile_group
      # Find prefix parent.
      words = ngram.split(' ')
      suffix = words.pop()
      while words:
        prefix = ' '.join(words)
        if prefix in ngram_map:
          last_leaf, last_count, last_scale, word_root = ngram_map[prefix]
          word_probability = count / last_count
          # Use this ngram to rescale prefix. If we learn the smallest n+1gram
          # is X then any *unknown* n+1grams should be at least that small.
          min_scale = min(last_scale, word_probability)  # This breaks %tiles.
          ngram_map[prefix] = (last_leaf, last_count, min_scale, word_root)
          break
        raise NotImplementedError('Unable to graft %s, no prefix' % ngram)
      else:
        # Unigram: add the entire `suffix` onto `root`.
        word_root = root
        word_probability = count / total_count
      leaf = _add(word_root, suffix, word_probability, True)
      ngram_map[ngram] = (leaf, count, min_scale, bloom_node.BloomNode())
  # Graft all of the ngram leaves back to root.
  scaled_roots = {}
  for leaf, _, scale, children in ngram_map.values():
    if scale not in scaled_roots:
      scaled_roots[scale] = root * scale
    loop_back = scaled_roots[scale]
    if children:
      loop_back += children
    leaf.link(' ', loop_back)


def _add(
    root: bloom_node.BloomNode,
    key: str,
    value: float,
    include_space: bool) -> bloom_node.BloomNode:
  l = len(key)
  pos = 0
  if include_space:
    char_masks_space = _char_masks(key, include_space)
  else:
    char_masks_space = []
  char_masks_base = _char_masks(key, False)
  cursor = root
  while pos <= l:
    if include_space:
      cursor.require(char_masks_space[pos])  # Provide space.
    cursor.require(char_masks_base[pos])
    cursor.distance(l - pos)
    cursor.weight(value, pos == l)
    if pos < l:
      cursor = cursor.open(key[pos])
    pos += 1
  return cursor


def _char_masks(s: str, include_space: bool) -> List[int]:
  result = [bloom_mask.REQUIRE_NOTHING]
  acc = 0
  if include_space:
    extra = bloom_mask.for_alpha(' ')
  else:
    extra = 0
  for c in s[::-1]:
    acc |= bloom_mask.for_alpha(c) | extra
    result.append(acc)
  return list(reversed(result))

"""Produce BloomNode graphs from words.

TODO: Create a root Trie which lazy-expands based on sibling length_mask.
"""
from typing import List

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


def _add(
    root: bloom_node.BloomNode,
    key: str,
    value: float,
    include_space: bool) -> bloom_node.BloomNode:
  l = len(key)
  pos = 0
  char_masks = _char_masks(key, include_space)
  cursor = root
  while pos <= l:
    cursor.require(char_masks[pos])
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

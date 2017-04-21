"""Library for working with words and word frequencies.

Intended to be used with data from  http://norvig.com/ngrams which is from:
  https://research.googleblog.com/2006/08/all-our-n-gram-are-belong-to-you.html
"""
import functools

import marisa_trie

from src.data import data


class Trie(marisa_trie.BytesTrie):
  def __getitem__(self, key):
    items = super(Trie, self).__getitem__(key)
    return [int.from_bytes(i, 'little') for i in items]


def load(input):
  arg = []
  weights = []
  for word, weight in input:
    arg.append((word, _as_bytes(weight)))
    weights.append(float(weight))
  return Trie(
        arg=arg,
        order=marisa_trie.WEIGHT_ORDER,
        weights=weights)


@functools.lru_cache(1)
def load_from_file(f):
  return load(_parse_file(f))


def _parse_file(f):
  for line in data.open_project_path(f):
    word, weight = line.split()
    yield word, int(weight) or 1


def _as_bytes(weight):
  byte_len = 0
  counter = weight
  while counter:
    byte_len += 1
    counter >>= 8
  return weight.to_bytes(byte_len, 'little')


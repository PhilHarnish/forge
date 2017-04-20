"""Library for working with words and word frequencies.

Intended to be used with data from  http://norvig.com/ngrams which is from:
  https://research.googleblog.com/2006/08/all-our-n-gram-are-belong-to-you.html
"""

import marisa_trie

from src.data import data

_DATA = None


def trie():
  global _DATA
  if not _DATA:
    _DATA = _load()
  return _DATA


def _load():
  arg = []
  weights = []
  for i, line in enumerate(data.open_project_path('data/count_1w.txt')):
    word, weight = line.split()
    word, weight = word, int(weight) or 1
    arg.append((word, _as_bytes(weight)))
    weights.append(float(weight))
  return marisa_trie.BytesTrie(
        arg=arg,
        order=marisa_trie.WEIGHT_ORDER,
        weights=weights)


def _as_bytes(weight):
  byte_len = 0
  counter = weight
  while counter:
    byte_len += 1
    counter >>= 8
  return weight.to_bytes(byte_len, 'little')


"""Library for working with words and word frequencies.

Intended to be used with data from  http://norvig.com/ngrams which is from:
  https://research.googleblog.com/2006/08/all-our-n-gram-are-belong-to-you.html
"""

import marisa
import marisa_trie

from src.data import data

_DATA = None

class _Trie(object):
  pass


class _CythonTrie(_Trie):
  def __init__(self, arg, weights):
    self._trie = marisa_trie.BytesTrie(
        arg=arg,
        order=marisa_trie.WEIGHT_ORDER,
        weights=weights)

  def __len__(self):
    return len(self._trie)

  def iteritems(self):
    for i in self._trie.iteritems():
      yield i


class _SwigTrie(_Trie):
  def __init__(self, arg, weights):
    keyset = marisa.Keyset()
    for (key, value), weight in zip(arg, weights):
      keyset.push_back(key, float(weight))
    self._trie = marisa.Trie()
    self._trie.build(keyset)

  def __len__(self):
    return self._trie.num_keys()

  def iteritems(self):
    agent = marisa.Agent()
    agent.set_query('')
    while self._trie.predictive_search(agent):
      yield agent.key_str()


def trie(klass=_CythonTrie):
  global _DATA
  if not _DATA:
    _DATA = _load(klass)
  return _DATA


def _load(klass):
  arg = []
  weights = []
  for i, line in enumerate(data.open_project_path('data/count_1w.txt')):
    word, weight = line.split()
    word, weight = word, int(weight) or 1
    arg.append((word, _as_bytes(weight)))
    weights.append(float(weight))
  return klass(arg=arg, weights=weights)


def _as_bytes(weight):
  byte_len = 0
  counter = weight
  while counter:
    byte_len += 1
    counter >>= 8
  return weight.to_bytes(byte_len, 'little')


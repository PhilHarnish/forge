import re

from data import anagram_index

_WORD_REGEX = re.compile(r'^\w+$', re.IGNORECASE)
_TRIE = {}
_ANAGRAM_INDEX = None
_LETTER_FREQUENCY = None


def init_trie(src):
  global _TRIE
  _TRIE = src


def reset():
  _TRIE = None
  _ANAGRAM_INDEX = None
  _FREQS = None


def score_word(word):
  if not _valid(word):
    return False
  if word in _TRIE:
    return 1
  return .1


def _valid(word):
  if not word:
    return False
  if not _WORD_REGEX.match(word):
    return False
  return True


def score_anagram(word):
  if not _valid(word):
    return 0
  index = _get_anagram_index()
  if word not in index:
    return 0
  return len(index[word]) > 1


def _get_anagram_index():
  global _ANAGRAM_INDEX
  if not _ANAGRAM_INDEX:
    _ANAGRAM_INDEX = anagram_index.AnagramIndex(_TRIE)
  return _ANAGRAM_INDEX


def score_cryptogram(word):
  if not _valid(word):
    return 0
  # TODO: Analyze letter frequencies.
  # TODO: Reject words which have impossible patterns (e.g. 'aaabaaa').
  return .1

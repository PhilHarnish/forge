import re

from data import anagram_index

_WORD_REGEX = re.compile(r'^\w+$', re.IGNORECASE)
_ANAGRAM_INDEX = None
_TRIE = {}


def init_trie(src):
  global _TRIE
  _TRIE = src


def score_word(word):
  if not word:
    return 0
  if not _WORD_REGEX.match(word):
    return 0
  if word in _TRIE:
    return 1
  return .1


def score_anagram(word):
  if not word:
    return 0
  if not _WORD_REGEX.match(word):
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

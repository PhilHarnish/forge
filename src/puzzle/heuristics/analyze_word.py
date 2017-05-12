import re

_WORD_REGEX = re.compile(r'^\w+$', re.IGNORECASE)
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

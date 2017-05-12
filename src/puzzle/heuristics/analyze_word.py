import re

from data import warehouse

_WORD_REGEX = re.compile(r'^\w+$', re.IGNORECASE)


def score_word(word):
  if not _valid(word):
    return False
  if word in warehouse.get('/words/unigram/trie'):
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
  index = warehouse.get('/words/unigram/anagram_index')
  if word not in index:
    return 0
  results = index[word]
  if len(results) > 1:
    return 1
  if word in results:
    return 0  # Input word == anagram word.
  return 1  # New word found.


def score_cryptogram(word):
  if not _valid(word):
    return 0
  # TODO: Analyze letter frequencies.
  # TODO: Reject words which have impossible patterns (e.g. 'aaabaaa').
  return .1

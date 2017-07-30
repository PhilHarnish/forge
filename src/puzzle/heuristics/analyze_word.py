import collections
import re

from data import warehouse

_WORD_REGEX = re.compile(r'^\w+$', re.IGNORECASE)


def score_word(word):
  if not _valid(word):
    return False
  if word in warehouse.get('/words/unigram'):
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
  last = word[0]
  streak = 1
  for c in word[1:]:
    if c == last:
      streak += 1
    else:
      last = c
      streak = 1
    if streak >= 3:
      return 0
  c = collections.Counter(word)
  length = len(word)
  threshold = length // 2
  n_letters = len(c)
  if length > 5 and (
      max(c.values()) > threshold or
      n_letters < threshold
  ):
    return 0
  return .1

import re

from src.data import data
from src.origen import seven_segment


class WordList(dict):

  def __init__(self, name, words):
    super(WordList, self).__init__()
    self.name = name
    for word in words:
      for variant in _enumerate_words(word):
        self[variant] = None

  def __getitem__(self, item):
    if super(WordList, self).__getitem__(item) is None:
      self[item] = glyphs_from_str(item)
    return super(WordList, self).__getitem__(item)


def _enumerate_words(word):
  result = []
  for candidate in [word, word[0].upper() + word[1:], word.upper()]:
    if _VALID_REGEX.match(candidate):
      result.append(candidate)
  return result


def glyphs_from_str(s):
  result = seven_segment.Glyphs(s, '')
  for c in s:
    result += ALPHABET[c]
  result.name = s
  return result


ALPHABET = data.load('data/seven_segment_alphabet.txt', seven_segment.Glyphs)
_VALID_REGEX = re.compile('^[%s]+$' % ''.join(ALPHABET.keys()))

ACCESS_WORDS = data.load('data/seven_segment_access_words.txt', WordList)
ACCESS = ACCESS_WORDS['POSITIVE']['ACCESS']


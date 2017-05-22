import collections

from data import anagram_index, crossword, data, trie, warehouse, \
  word_frequencies
from puzzle.heuristics import analyze


# Data sources.
def _get_words_top():
  result = collections.OrderedDict()
  for row in open(data.project_path('data/words_coca.txt')):
    rank, word, part, freq, dispersion = row.rstrip('\n').split()
    if word.isalpha():
      result[word.lower()] = freq
  return result


_TRUNCATION_LIMIT = 2 ** 27

def _get_unigram():
  results = []
  top_words = warehouse.get('/words/top')
  for word, value in word_frequencies.parse_file('data/count_1w.txt'):
    l = len(word)
    if word not in top_words:
      reduction_factor = _TRUNCATION_LIMIT >> (l ** 2) or 1
      value = value // reduction_factor
    if value:
      results.append((word, value))
  return collections.OrderedDict(
      sorted(results, key=lambda x: x[1], reverse=True))


def _get_unigram_anagram_index():
  return anagram_index.AnagramIndex(warehouse.get('/words/unigram'))


def _get_unigram_trie():
  return trie.Trie(warehouse.get('/words/unigram').items())


def _get_crossword():
  return crossword.connect('data/crossword.sqlite')


def _get_crossword_connection():
  connection, cursor = warehouse.get('/phrases/crossword')
  del cursor
  return connection


def _get_crossword_cursor():
  connection, cursor = warehouse.get('/phrases/crossword')
  del connection
  return cursor


def init():
  analyze.init()
  warehouse.init()
  warehouse.register('/phrases/crossword', _get_crossword)
  warehouse.register('/phrases/crossword/connection', _get_crossword_connection)
  warehouse.register('/phrases/crossword/cursor', _get_crossword_cursor)
  warehouse.register('/words/top', _get_words_top)
  warehouse.register('/words/unigram', _get_unigram)
  warehouse.register('/words/unigram/anagram_index', _get_unigram_anagram_index)
  warehouse.register('/words/unigram/trie', _get_unigram_trie, pickle=True)


def reset():
  analyze.reset()
  warehouse.reset()

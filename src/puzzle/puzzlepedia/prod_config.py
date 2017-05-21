import collections

from data import anagram_index, crossword, trie, warehouse, word_frequencies
from puzzle.heuristics import analyze


# Data sources.
def _get_unigram():
  return collections.OrderedDict(
      word_frequencies.parse_file('data/count_1w.txt'))


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
  warehouse.register('/words/unigram', _get_unigram)
  warehouse.register('/words/unigram/anagram_index', _get_unigram_anagram_index)
  warehouse.register('/words/unigram/trie', _get_unigram_trie)


def reset():
  analyze.reset()
  warehouse.reset()

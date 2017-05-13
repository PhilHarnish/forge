from data import anagram_index, crossword, warehouse, word_frequencies


# Data sources.
def _get_unigram_anagram_index():
  return anagram_index.AnagramIndex(warehouse.get('/words/unigram/trie'))


def _get_unigram_trie():
  return word_frequencies.load_from_file('data/count_1w.txt')


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
  warehouse.init()
  warehouse.register('/phrases/crossword', _get_crossword)
  warehouse.register('/phrases/crossword/connection', _get_crossword_connection)
  warehouse.register('/phrases/crossword/cursor', _get_crossword_cursor)
  warehouse.register('/words/unigram/anagram_index', _get_unigram_anagram_index)
  warehouse.register('/words/unigram/trie', _get_unigram_trie)

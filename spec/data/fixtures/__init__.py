from data import anagram_index, crossword
from data import warehouse
from spec.data.fixtures import tries


def _get_unigram_anagram_index():
  return anagram_index.AnagramIndex(warehouse.get('/words/unigram/trie'))

def _get_unigram_trie():
  return tries.ambiguous()

def _get_crossword():
  connection = crossword.init(':memory:')
  return connection, connection.cursor()

def _get_crossword_connection():
  connection, cursor = warehouse.get('/phrases/crossword')
  del cursor
  return connection

def _get_crossword_cursor():
  connection, cursor = warehouse.get('/phrases/crossword')
  del connection
  return cursor

warehouse.init()
warehouse.register('/phrases/crossword', _get_crossword)
warehouse.register('/phrases/crossword/connection', _get_crossword_connection)
warehouse.register('/phrases/crossword/cursor', _get_crossword_cursor)
warehouse.register('/words/unigram/anagram_index', _get_unigram_anagram_index)
warehouse.register('/words/unigram/trie', _get_unigram_trie)

import collections

from data import anagram_index, crossword, warehouse
from spec.data.fixtures import tries


def _get_unigram():
  return collections.OrderedDict(tries.kitchen_sink_data())

def _get_unigram_anagram_index():
  return anagram_index.AnagramIndex(warehouse.get('/words/unigram'))

def _get_unigram_trie():
  return tries.kitchen_sink()

def _get_crossword():
  connection = crossword.init(':memory:')
  cursor = connection.cursor()
  crossword.add(cursor, 'query', 1, {'ask': 1, 'question': 1})
  return connection, cursor

def _get_crossword_connection():
  connection, cursor = warehouse.get('/phrases/crossword')
  del cursor
  return connection

def _get_crossword_cursor():
  connection, cursor = warehouse.get('/phrases/crossword')
  del connection
  return cursor


def init():
  """Available for functions which need to preserve imports."""
  pass

warehouse.init()
warehouse.register('/phrases/crossword', _get_crossword)
warehouse.register('/phrases/crossword/connection', _get_crossword_connection)
warehouse.register('/phrases/crossword/cursor', _get_crossword_cursor)
warehouse.register('/words/unigram', _get_unigram)
warehouse.register('/words/unigram/anagram_index', _get_unigram_anagram_index)
warehouse.register('/words/unigram/trie', _get_unigram_trie)

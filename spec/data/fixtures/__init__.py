import collections

from data import crossword, warehouse
from data.anagram import anagram_index
from spec.data.fixtures import _words_api, tries


# API sources.
def _get_words_api():
  return _words_api


# Image sources.
def _get_image_components():
  return {}


# Data sources.
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
warehouse.register('/api/words', _get_words_api)
warehouse.register('/image/components', _get_image_components)
warehouse.register('/phrases/crossword', _get_crossword)
warehouse.register('/phrases/crossword/connection', _get_crossword_connection)
warehouse.register('/phrases/crossword/cursor', _get_crossword_cursor)
warehouse.register('/words/unigram', _get_unigram)
warehouse.register('/words/unigram/anagram_index', _get_unigram_anagram_index)
warehouse.register('/words/unigram/trie', _get_unigram_trie)

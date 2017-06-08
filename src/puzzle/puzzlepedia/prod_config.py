import collections

from data import anagram_index, crossword, data, pickle_cache, trie, \
  warehouse, \
  word_frequencies
from data.word_api import word_api
from puzzle.heuristics import analyze

_DEADLINE_MS = 5000


# API sources.
def _get_words_api():
  return word_api.get_api('wordnet')


# Data sources.
def _get_words_top():
  result = collections.OrderedDict()
  for row in open(data.project_path('data/words_coca.txt')):
    rank, word, part, freq, dispersion = row.rstrip('\n').split()
    if word.isalpha():
      result[word.lower()] = freq
  return result


_TRUNCATION_LIMIT = 2 ** 27
_WORD_LIMIT = 47436  # After "gherkin" which is a cryptic solution in test set.

def _get_unigram():
  results = []
  top_words = warehouse.get('/words/top')
  for word, value in word_frequencies.parse_file('data/count_1w.txt'):
    if value < _WORD_LIMIT:
      break
    last_c = None
    c_chain = 0
    for c in word:
      if c == last_c:
        c_chain += 1
      else:
        last_c = c
        c_chain = 1
      if c_chain >= 3:
        break
    else:
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


@pickle_cache.cache('words_unigram_trie')
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
  warehouse.init(deadline_ms=_DEADLINE_MS)
  warehouse.register('/api/words', _get_words_api)
  warehouse.register('/phrases/crossword', _get_crossword)
  warehouse.register('/phrases/crossword/connection', _get_crossword_connection)
  warehouse.register('/phrases/crossword/cursor', _get_crossword_cursor)
  warehouse.register('/words/top', _get_words_top)
  warehouse.register('/words/unigram', _get_unigram)
  warehouse.register('/words/unigram/anagram_index', _get_unigram_anagram_index)
  warehouse.register('/words/unigram/trie', _get_unigram_trie)


def reset():
  analyze.reset()
  warehouse.reset()

import collections

from data import crossword, data, pickle_cache, trie, warehouse, \
  word_frequencies
from data.anagram import anagram_index
from data.graph import bloom_node, trie as graph_trie
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


def _get_bigram():
  results = {}  # NB: Not sorted.
  for word, value in word_frequencies.parse_file('data/count_2w.txt'):
    if value:
      word = word.lower()
      if word in results:
        results[word] = max(results[word], value)
      else:
        results[word] = value
  return results


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


def _get_words(length_mask: int = None, file: str = 'data/g1m_1gram.txt') -> list:
  for word, value in word_frequencies.parse_file(file):
    if len(word) > 12:
      continue
    elif not word.isalpha():
      continue
    if length_mask and (1 << len(word)) & length_mask == 0:
      continue
    yield word, value


def _get_ngrams() -> bloom_node.BloomNode:
  ngrams = [list(_get_words())]
  for i in range(2, 5+1):
    ngrams.append(list(_get_words(file='data/coca_%sgram.txt' % i)))
  root = bloom_node.BloomNode()
  graph_trie.add_ngrams(root, ngrams)
  return root


def init() -> None:
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
  warehouse.register('/words/bigram', _get_bigram)
  warehouse.register('/graph/ngram', _get_ngrams)


def reset() -> None:
  analyze.reset()
  warehouse.reset()

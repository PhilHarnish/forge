from data import anagram_index
from data import warehouse
from spec.data.fixtures import tries


def _get_unigram_anagram_index():
  return anagram_index.AnagramIndex(warehouse.get('/words/unigram/trie'))

def _get_unigram_trie():
  return tries.ambiguous()

warehouse.init()
warehouse.register('/words/unigram/anagram_index', _get_unigram_anagram_index)
warehouse.register('/words/unigram/trie', _get_unigram_trie)

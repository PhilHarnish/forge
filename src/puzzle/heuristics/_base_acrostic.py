from data import warehouse
from data.seek_sets import seek_set


class BaseAcrostic(object):
  def __init__(self, words, trie=None):
    self._trie = trie or warehouse.get('/words/unigram/trie')
    if isinstance(words, seek_set.SeekSet):
      self._words = words
    else:
      self._words = seek_set.SeekSet(words)

  def subscribe(self, observer):
    raise NotImplementedError()

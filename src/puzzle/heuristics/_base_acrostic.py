from data import warehouse


class BaseAcrostic(object):
  def __init__(self, words, trie=None):
    self._trie = trie or warehouse.get('/words/unigram/trie')
    self._words = [set(word) for word in words]

  def subscribe(self, observer):
    raise NotImplementedError()

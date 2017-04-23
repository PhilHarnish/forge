import marisa_trie


class Trie(marisa_trie.BytesTrie):
  def __init__(self, input):
    arg = []
    weights = []
    for word, weight in input:
      arg.append((word, _as_bytes(weight)))
      weights.append(float(weight))
    super(Trie, self).__init__(
        arg=arg,
        order=marisa_trie.WEIGHT_ORDER,
        weights=weights)

    # Must implement:
    self.has_keys_with_prefix = self.has_keys_with_prefix
    self.__contains__ = self.__contains__
    self.__len__ = self.__len__
    assert self.__getitem__

  def __getitem__(self, key):
    items = super(Trie, self).__getitem__(key)
    return int.from_bytes(items[0], 'little')


def _as_bytes(weight):
  byte_len = 0
  counter = weight
  while counter:
    byte_len += 1
    counter >>= 8
  return weight.to_bytes(byte_len, 'little')

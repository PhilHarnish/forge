from data.seek_sets import base_seek_set

_FULL_ALPHABET = set('abcdefghijklmnopqrstuvwxyz')


class CryptoSeekSet(base_seek_set.BaseSeekSet):
  def __init__(self, sets, translation=None):
    if not isinstance(sets, str):
      raise TypeError('CryptoSeekSet `sets` must be str')
    super(CryptoSeekSet, self).__init__(sets)
    if translation:
      # Initialize with "translation".
      # Invert map; we want to quickly convert crypto
      self._crypto_to_normal = translation.copy()
      self._normal_to_crypto = {v: k for k, v in translation.items()}
    else:
      self._crypto_to_normal = {}
      self._normal_to_crypto = {}

  def __contains__(self, seek):
    if len(seek) == 0:
      # Beginning of set; always True.
      return True
    return super(CryptoSeekSet, self).__contains__(seek)

  def seek(self, seek):
    end = len(seek)
    l = len(self._sets)
    if end == 0 and l:
      return _FULL_ALPHABET
    if end == l:
      # Even if it the 'seek' doesn't match our sets an iterative algorithm
      # should not raise IndexError. A complete match leaves no free letters.
      return set()
    if end > l:
      # Indicates a bug or inefficient behavior.
      raise IndexError('%s out of bounds' % seek)
    normal_to_crypto = self._normal_to_crypto.copy()
    crypto_to_normal = self._crypto_to_normal.copy()
    crypto = self._sets
    for pos, c in enumerate(seek):
      crypto_c = crypto[pos]
      if c in normal_to_crypto:
        if normal_to_crypto[c] != crypto_c:
          return set()
        continue  # Input and our translated copy line up.
      if crypto_c in crypto_to_normal:
        if crypto_to_normal[crypto_c] != c:
          # The crypto letter should have been c and was not.
          return set()
        continue
      # From now on this letter needs to match our underlying cryptogram.
      normal_to_crypto[c] = crypto_c
      crypto_to_normal[crypto_c] = c
    # Made it to the end of the input and it is valid.
    result = set()
    if crypto[end] in crypto_to_normal:
      # The next letter is already known.
      result.add(crypto_to_normal[crypto[end]])
    else:
      # The next letter is unknown.
      for c in _FULL_ALPHABET:
        if c not in normal_to_crypto:
          result.add(c)
    return result

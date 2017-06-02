from data.seek_sets import base_seek_set

_FULL_ALPHABET = set('abcdefghijklmnopqrstuvwxyz')


class CryptoSeekSet(base_seek_set.BaseSeekSet):
  def __init__(self, sets, translation=None):
    if not isinstance(sets, str):
      raise TypeError('CryptoSeekSet `sets` must be str')
    super(CryptoSeekSet, self).__init__(sets)
    if translation:
      # Invert map; we want to quickly convert crypto
      self._translation = {v: k for k, v in translation.items()}
    else:
      self._translation = {}

  def __contains__(self, seek):
    if len(seek) == 0:
      # Beginning of set; always True.
      return True
    raise NotImplementedError()

  def __getitem__(self, seek):
    if isinstance(seek, slice):
      start, stop, step = seek.start, seek.stop, seek.step
    elif isinstance(seek, int):
      start, stop, step = seek, seek, 1
    else:
      start, stop, step = None, None, None
    if start is not None:  # Slicing.
      if start == 0:
        return self
      else:
        # TODO: Find a way to support this? Seems impossible.
        raise IndexError('%s out of bounds' % seek)
    # Indexing for lookup.
    return self.seek(seek)

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
    working_set = self._translation.copy()
    sets = self._sets
    for pos, c in enumerate(seek):
      if c in working_set:
        if working_set[c] != sets[pos]:
          return set()
        continue  # Input and our translated copy line up.
      # From now on this letter needs to match our underlying cryptogram.
      working_set[c] = sets[pos]
    # Made it to the end of the input.
    result = set()
    for c in _FULL_ALPHABET:
      if c not in working_set:
        result.add(c)
    return result

  def __len__(self):
    return len(self._sets)

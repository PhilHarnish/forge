import collections

_FULL_ALPHABET = set('abcdefghijklmnopqrstuvwxyz')


class SeekSet(object):
  def __init__(self, sets, sets_permutable=False, indexes=None,
      indexes_permutable=False):
    if indexes_permutable and not indexes:
      raise IndexError('Must specify indexes if indexes_permutable=True')
    if indexes:
      if not indexes_permutable and not sets_permutable:
        # Use indexes to filter down sets then throw away indexes.
        for i, s in enumerate(sets):
          index = indexes[i]
          if index:
            # Truncate sets[i] to a single letter from sets[i].
            sets[i] = sets[i][indexes[i] - 1]
        indexes = None
      elif indexes_permutable:
        raise NotImplementedError()
    self._sets = list(sets)
    self._sets_permutable = sets_permutable
    self._indexes = indexes
    self._indexes_permutable = indexes_permutable
    if sets_permutable or indexes_permutable:
      self._seek_trie = {}
      self._set_index = _index_sets(indexes, sets)
    else:
      self._seek_trie = None
      self._set_index = None

  def __getitem__(self, seek):
    """Use `seek` to index into `self` and return set of available letters."""
    if isinstance(seek, slice):
      start, stop, step = seek.start, seek.stop, seek.step
    elif isinstance(seek, int):
      start, stop, step = seek, seek, 1
    else:
      start, stop, step = None, None, None
    if start is not None:
      if start == 0:
        return self
      elif not self._sets_permutable and not self._indexes_permutable:
        return SeekSet(self._sets[start:stop:step])
      else:
        # TODO: Find a way to support this? Seems impossible.
        return SeekSet([[]])
    # Indexing for lookup.
    return self.seek(seek)

  def seek(self, seek):
    result = set()
    if not self._indexes:
      if not self._sets_permutable:
        # Trivial case.
        for i, c in enumerate(seek):
          if c not in self._sets[i]:
            return result
        return set(self._sets[len(seek)])
      if len(seek) == 0:
        # Beginning of SeekSet; all letters are available.
        return set(self._set_index[None].keys())
    try:
      _visit(
          result, set(), self._sets, self._set_index, self._indexes, seek, 0,
          False)
    except:
      pass
    return result

  def __contains__(self, seek):
    if len(seek) == 0:
      # Beginning of SeekSet; always True.
      return True
    if not self._indexes and not self._sets_permutable:
      # Trivial case.
      for i, c in enumerate(seek):
        if c not in self._sets[i]:
          return False
      return True
    try:
      _visit(
          set(), set(), self._sets, self._set_index, self._indexes, seek, 0,
          True)
      return False
    except StopIteration:
      return True

  def __len__(self):
    return len(self._sets)


def _index_sets(indexes, sets):
  result = {}
  if indexes is None:
    result[None] = _index_all(sets)
  else:
    for index in indexes:
      if index is None:
        result[index] = _index_all(sets)
      else:
        index -= 1
        char_map = collections.defaultdict(set)
        result[index] = char_map
        for i, chars in enumerate(sets):
          if chars is None:
            for char in _FULL_ALPHABET:
              char_map[char].add(i)
          elif index < len(chars):
            char_map[chars[index]].add(i)
  return result


def _index_all(sets):
  char_map = collections.defaultdict(set)
  for i, chars in enumerate(sets):
    if chars is None:
      chars = _FULL_ALPHABET
    for c in chars:
      char_map[c].add(i)
  return char_map


def _visit(result, visited, sets, set_index, indexes, seek, pos, stop):
  if indexes and pos >= len(indexes) and stop:
    raise StopIteration()  # End of the line.
  if indexes is None or indexes[pos] is None:
    index = None
  else:
    index = indexes[pos] - 1
  if pos == len(seek):
    for i, set in enumerate(sets):
      if i in visited:
        continue
      elif set is None:
        result.update(_FULL_ALPHABET)
        raise StopIteration()
      elif index is None:
        result.update(c for c in set)
      elif index < len(set):
        result.add(set[index])
    if stop:
      raise StopIteration()  # Found at least one path.
    elif len(result) == len(set_index[index]):
      raise StopIteration()  # All characters added.
    return
  c = seek[pos]
  if c not in set_index[index]:
    return  # Invalid character.
  for next_visit in set_index[index][c]:
    if next_visit in visited:
      continue
    visited.add(next_visit)
    _visit(result, visited, sets, set_index, indexes, seek, pos + 1, stop)
    visited.remove(next_visit)

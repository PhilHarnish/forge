import collections

from data.seek_sets import base_seek_set

_FULL_ALPHABET = set('abcdefghijklmnopqrstuvwxyz')


class SeekSet(base_seek_set.BaseSeekSet):
  def __init__(self, sets, sets_permutable=False, indexes=None,
      indexes_permutable=False, start_seek=None):
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
    super(SeekSet, self).__init__(sets)
    self._sets_permutable = sets_permutable
    self._indexes = indexes
    self._indexes_permutable = indexes_permutable
    if sets_permutable or indexes_permutable:
      self._seek_trie = {}
      self._set_index = _index_sets(indexes, sets)
    else:
      self._seek_trie = None
      self._set_index = None
    self._start_seek = start_seek

  def _slice(self, start, stop, step):
    if start == 0:
      return self
    elif not self._sets_permutable and not self._indexes_permutable:
      return SeekSet(self._sets[start:stop:step])
    elif isinstance(start, int):
      raise IndexError('%s out of bounds' % start)
    # Degenerate case is really inefficient: instantiate a SeekSet which starts
    # at "start".
    return SeekSet(
        self._sets, sets_permutable=self._sets_permutable,
        indexes=self._indexes, indexes_permutable=self._indexes_permutable,
        start_seek=list(start),
    )

  def seek(self, seek):
    if self._start_seek:
      seek = self._start_seek + seek
    result = set()
    end = len(seek)
    l = len(self._sets)
    if end == l:
      return result
    elif end > l:
      # Indicates a bug or inefficient behavior.
      raise IndexError('%s out of bounds' % seek)
    if not self._indexes:
      if not self._sets_permutable:
        # Trivial case.
        for i, c in enumerate(seek):
          if c not in self._sets[i]:
            return result
        return set(self._sets[end])
      if end == 0:
        # Beginning of SeekSet; all letters are available.
        return set(self._set_index[None].keys())
    try:
      _visit(
          result, [False] * l, self._sets, self._set_index,
          self._indexes, seek, 0, False)
    except StopIteration:
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
          set(), [False] * len(self._sets), self._sets, self._set_index,
          self._indexes, seek, 0, True)
      return False
    except StopIteration:
      return True

  def __len__(self):
    if self._indexes:
      return min(len(self._indexes), super(SeekSet, self).__len__())
    return super(SeekSet, self).__len__()


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
  if indexes and pos >= len(indexes):
    raise StopIteration()  # End of the line.
  if indexes is None or indexes[pos] is None:
    index = None
  else:
    index = indexes[pos] - 1
  if pos == len(seek):
    for i, set in enumerate(sets):
      if visited[i]:
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
    if visited[next_visit]:
      continue
    visited[next_visit] = True
    _visit(result, visited, sets, set_index, indexes, seek, pos + 1, stop)
    visited[next_visit] = False

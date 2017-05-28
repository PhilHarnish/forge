import collections


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
      self._set_index = self._index_sets(sets)
    else:
      self._seek_trie = None
      self._set_index = None

  def __getitem__(self, seek):
    """Use `seek` to index into `self` and return set of available letters."""
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
        return set(self._set_index.keys())
    _visit(result, set(), self._sets, self._set_index, self._indexes, seek, 0)
    return result

  def __len__(self):
    return len(self._sets)

  def _index_sets(self, sets):
    result = collections.defaultdict(set)
    for i, chars in enumerate(sets):
      for c in chars:
        result[c].add(i)
    return result


class _SeekCursor(SeekSet):
  def __getitem__(self, item):
    raise NotImplementedError()


def _visit(result, visited, sets, set_index, indexes, seek, pos):
  if indexes is None or indexes[pos] is None:
    index = None
  else:
    index = indexes[pos] - 1
  if pos == len(seek):
    for i, set in enumerate(sets):
      if i in visited:
        continue
      if index is None:
        result.update(c for c in set)
      elif index < len(set):
        result.add(set[index])
    return  # End of the line.
  if len(result) == len(set_index):
    return  # All characters added.
  c = seek[pos]
  if c not in set_index:
    return  # Invalid character.
  for next_visit in set_index[c]:
    if next_visit in visited:
      continue
    if index is not None and index >= len(sets[next_visit]):
      continue
    visited.add(next_visit)
    _visit(result, visited, sets, set_index, indexes, seek, pos + 1)
    visited.remove(next_visit)

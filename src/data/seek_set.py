import collections


class SeekSet(object):
  def __init__(self, sets, sets_permutable=False, indexes=None,
      indexes_permutable=False):
    self._sets = list(sets)
    self._sets_permutable = sets_permutable
    if indexes_permutable and not indexes:
      raise IndexError('Must specify indexes if indexes_permutable=True')
    if indexes or indexes_permutable:
      raise NotImplementedError()
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
    if not self._sets_permutable and not self._indexes:
      # Trivial case.
      return set(self._sets[len(seek)])
    end_pos = len(seek)
    if len(seek) == 0:
      # Beginning of SeekSet; all letters are available.
      return set(self._set_index.keys())
    result = set()

    def visit(result, visited, set_index, seek, pos):
      if pos == end_pos:
        for i, set in enumerate(self._sets):
          if i in visited:
            continue
          result.update(c for c in set)
        return  # End of the line.
      if len(result) == len(set_index):
        return  # All characters added.
      c = seek[pos]
      if c not in set_index:
        return []  # Invalid character.
      for next_visit in set_index[c]:
        if next_visit in visited:
          continue
        visited.add(next_visit)
        visit(result, visited, set_index, seek, pos + 1)
        visited.remove(next_visit)

    visit(result, set(), self._set_index, seek, 0)
    return result

  def _index_sets(self, sets):
    result = collections.defaultdict(set)
    for i, chars in enumerate(sets):
      for c in chars:
        result[c].add(i)
    return result


class _SeekCursor(SeekSet):
  def __getitem__(self, item):
    raise NotImplementedError()

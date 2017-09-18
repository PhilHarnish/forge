class BaseSeekSet(object):
  def __init__(self, sets):
    self._sets = list(sets)

  def __contains__(self, item):
    raise NotImplementedError()

  def __getitem__(self, seek):
    """Use `seek` to index into `self` and return set of available letters."""
    if isinstance(seek, slice):
      start, stop, step = seek.start, seek.stop, seek.step
    elif isinstance(seek, int):
      start, stop, step = seek, seek, 1
    else:
      start, stop, step = None, None, None
    if start is None:
      # Indexing for lookup.
      return self.seek(seek)
    # Slicing.
    return self._slice(start, stop, step)

  def _slice(self, start, stop, step):
    if not start:
      return self
    raise IndexError('Index "%s" out of bounds' % start)

  def __len__(self):
    return len(self._sets)

  def seek(self, seek):
    raise NotImplementedError()

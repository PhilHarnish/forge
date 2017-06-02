class BaseSeekSet(object):
  def __init__(self, sets):
    self._sets = list(sets)

  def __len__(self):
    return len(self._sets)

  def seek(self, seek):
    raise NotImplementedError()

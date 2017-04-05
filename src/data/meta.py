import collections


class Meta(collections.OrderedDict):
  def __init__(self, *args, **kwargs):
    super(Meta, self).__init__(*args, **kwargs)
    self._ordered = False

  def __setitem__(self, key, value, *args, **kwargs):
    super(Meta, self).__setitem__(key, value, *args, **kwargs)
    self._ordered = False

  def items(self):
    self._reorder()
    return super(Meta, self).items()

  def first(self):
    self._reorder()
    for k, v in self.items():
      return k, v

  def peek(self):
    self._reorder()
    for first in self:
      return first

  def _reorder(self):
    if self._ordered:
      return
    order = sorted(super(Meta, self).items(), key=lambda x: x[1], reverse=True)
    for k, v in order:
      self.move_to_end(k)
    self._ordered = True

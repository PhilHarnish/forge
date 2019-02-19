import collections
import typing


class Meta(collections.OrderedDict, typing.MutableMapping[str, float]):
  def __init__(self, *args, **kwargs) -> None:
    self._smallest = float('inf')
    self._largest = 0
    self._ordered = True
    super(Meta, self).__init__(*args, **kwargs)

  def __setitem__(self, key: str, value: float) -> None:
    if key in self and self[key] == value:
      raise AssertionError('Redundant assignment: %s = %s' % (key, value))
    if value > self._smallest:
      self._ordered = False
    else:
      self._smallest = value
    if value > self._largest:
      self._largest = value
    super(Meta, self).__setitem__(key, value)
    self._changed()

  def items(self) -> typing.ItemsView[str, float]:
    self._reorder()
    return super(Meta, self).items()

  def first(self) -> typing.Tuple[str, float]:
    self._reorder()
    for k, v in self.items():
      return k, v

  def peek(self) -> str:
    self._reorder()
    for first in self:
      return first

  def magnitude(self) -> float:
    return self._largest

  def _reorder(self) -> None:
    if self._ordered:
      return
    order = sorted(super(Meta, self).items(), key=lambda x: x[1], reverse=True)
    for k, v in order:
      self.move_to_end(k)
    self._ordered = True

  def _changed(self):
    pass

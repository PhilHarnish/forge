from typing import TypeVar

T = TypeVar('T')  # Generic type.


class FixedDict(dict):
  def __init__(self, size:int) -> None:
    if size <= 0: raise ValueError('size must be 1+')
    super(FixedDict, self).__init__()
    self._cursor = 0
    self._keys = [None] * size

  def __setitem__(self, key:str, value:T) -> None:
    new_key = key not in self
    if new_key:
      last_key = self._keys[self._cursor]
      if last_key is not None:
        del self[last_key]
    super(FixedDict, self).__setitem__(key, value)
    if new_key:
      self._keys[self._cursor] = key
      self._cursor = (self._cursor + 1) % len(self._keys)

from typing import List


_POOL = {}


def reset() -> None:
  _POOL.clear()


class Pooled(object):
  __slots__ = ('_pool',)

  def __init__(self, *args, **kwargs) -> None:
    del kwargs
    del args
    self._pool = _get_pool(type(self))

  def alloc(self, *args, **kwargs) -> 'Pooled':
    if self._pool:
      result = self._pool.pop()
      result.__init__(*args, **kwargs)
      return result
    return self._alloc(*args, **kwargs)

  def _alloc(self, *args, **kwargs) -> 'Pooled':
    raise NotImplementedError()

  def free(self) -> None:
    self._pool.append(self)


def _get_pool(t) -> List[Pooled]:
  if t not in _POOL:
    _POOL[t] = []
  return _POOL[t]

from typing import List


_POOL = {}


def reset() -> None:
  _POOL.clear()


class Pooled(object):
  __slots__ = ('_pool',)

  def __init__(self) -> None:
    self._pool = _get_pool(type(self))

  def alloc(self) -> 'Pooled':
    if self._pool:
      return self._pool.pop()
    return self._alloc()

  def _alloc(self) -> 'Pooled':
    raise NotImplementedError()

  def free(self) -> None:
    self._pool.append(self)


def _get_pool(t) -> List[Pooled]:
  if t not in _POOL:
    _POOL[t] = []
  return _POOL[t]

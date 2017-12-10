from typing import Dict, Optional

from data import types
from data.seek import base_seek, node


class SeekCursor(object):
  __slots__ = ('_host', '_path', '_node')

  def __init__(
      self, host: 'base_seek.BaseSeek', path: types.Path, n: node.Node):
    self._host = host
    self._path = path
    self._node = n

  def has_children(self) -> bool:
    return bool(len(self._node))

  def children(self) -> Dict[str, node.Node]:
    return self._node.children()

  def seek(self, edge: str) -> 'SeekCursor':
    n = self._node.get(edge)
    if n is None:
      raise KeyError(edge)
    return SeekCursor(self._host, (edge, self._path), n)

  def match(self) -> Optional[types.WeightedWord]:
    weight = self._node.match_weight()
    if weight:
      acc = []
      cursor = self._path
      while cursor:
        c, cursor = cursor
        acc.append(c)
      return ''.join(acc[::-1]), weight
    return None

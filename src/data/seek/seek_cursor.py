from typing import Any, List, Optional

from data.seek import base_seek
from data.trie2 import node, trie2


class SeekCursor(object):
  __slots__ = ('_parent', '_node', '_state')

  def __init__(self, parent: 'base_seek.BaseSeek', n: node.Node, state: Any):
    self._parent = parent
    self._node = n
    self._state = state

  def outgoing(self) -> List['SeekCursor']:
    raise NotImplementedError()

  def has_children(self) -> bool:
    raise NotImplementedError()

  def seek(self, next) -> 'SeekCursor':
    raise NotImplementedError()

  def match(self) -> Optional['trie2.WeightedWord']:
    raise NotImplementedError()

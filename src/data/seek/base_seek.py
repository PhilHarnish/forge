from data.seek import node, seek_cursor


class BaseSeek(object):
  __slots__ = ('_cursor_type', '_root')

  def __init__(
      self,
      root: node.Node,
      cursor_type: type(seek_cursor.SeekCursor) = seek_cursor.SeekCursor):
    self._root = root
    self._cursor_type = cursor_type

  def root(self) -> node.Node:
    return self._root

  def start(self) -> seek_cursor.SeekCursor:
    return self._cursor_type(self, None, self._root)

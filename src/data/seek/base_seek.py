from data.seek import node, seek_cursor


class BaseSeek(object):
  _cursor_type = seek_cursor.SeekCursor

  def __init__(self, root: node.Node):
    self._root = root

  def start(self) -> seek_cursor.SeekCursor:
    return self._cursor_type(self, None, self._root)

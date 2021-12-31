from puzzle.stream import stream_manager


class Q(object):
  def __init__(self):
    self._stream_manager = stream_manager.StreamManager()
    super(Q, self).__init__()

  def input(self, *args, **kwargs):
    list_args = []
    other_args = []
    for i in args:
      if isinstance(i, list):
        list_args.append(i)
      else:
        other_args.append(i)
    if list_args and other_args:
      raise TypeError('Ambiguous input args: %s' % args)
    elif list_args:
      for i in list_args:
        self._stream_manager.register_stream(None, i)
    elif other_args:
      self._stream_manager.register_stream(None, other_args)
    for k, v in kwargs.items():
      self._stream_manager.register_stream(k, v)

  def get_streams(self):
    return self._stream_manager.get_streams()

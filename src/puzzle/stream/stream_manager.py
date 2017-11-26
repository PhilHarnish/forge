class StreamManager(object):
  def __init__(self):
    self._next_stream_id = 0
    self._streams = {}

  def register_stream(self, name, data):
    if name is None:
      name = '_%s' % self._next_stream_id
      self._next_stream_id += 1
    self._streams[name] = data

  def get_streams(self):
    return self._streams

from data import meta, stream


class ObservableMeta(meta.Meta):
  def __init__(self, *args, **kwargs):
    super(ObservableMeta, self).__init__(*args, **kwargs)
    self._stream = stream.Stream()

  def subscribe(self, observer):
    self._stream.subscribe(observer)

  def _changed(self):
    self._stream.publish_value(self)

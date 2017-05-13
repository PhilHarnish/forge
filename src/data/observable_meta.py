from rx import subjects

from data import meta


class ObservableMeta(meta.Meta):
  def __init__(self, *args, **kwargs):
    super(ObservableMeta, self).__init__(*args, **kwargs)
    self.subject = subjects.Subject()

  def subscribe(self, observer):
    self.subject.subscribe(observer)

  def _changed(self):
    self.subject.on_next(self)

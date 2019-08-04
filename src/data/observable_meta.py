from rx import subjects

from data import meta, types


class ObservableMeta(meta.Meta[meta.Key]):
  def __init__(self, *args, **kwargs) -> None:
    super(ObservableMeta, self).__init__(*args, **kwargs)
    self.subject = subjects.Subject()

  def subscribe(self, observer: types.Observer) -> None:
    self.subject.subscribe(observer)

  def _changed(self) -> None:
    self.subject.on_next(self)

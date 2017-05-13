import rx


class Stream(rx.AnonymousObservable):
  def __init__(self):
    super(Stream, self).__init__(self._subscribe_impl)
    # TODO: WeakRef here is ideal but causes test failures?
    self._observers = set()

  def _subscribe_impl(self, observer):
    self._observers.add(observer)

  def publish_value(self, value):
    for observer in self._observers:
      observer.on_next(value)

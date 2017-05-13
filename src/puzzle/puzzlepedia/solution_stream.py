import rx
from rx import subjects


class SolutionStream(subjects.Subject):
  def __init__(self, address, solutions, children=None):
    super(SolutionStream, self).__init__()
    self._address = address
    self._stream = solutions.subject.map(self._on_solution_stream)
    if children:
      # If children streams are present, map & combine them with our stream.
      self._stream = self._stream.merge(
          rx.Observable.merge(*children).map(self._on_children_stream))
    # Route events from self._stream back into and out of ourselves.
    self._stream.subscribe(self)

  def _on_solution_stream(self, e):
    return (self._address, e)

  def _on_children_stream(self, e):
    child_address, child_value = e
    return (self._address + '.' + child_address, child_value)

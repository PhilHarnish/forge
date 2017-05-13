from rx import subjects


class SolutionStream(subjects.Subject):
  def __init__(self, address, solutions):
    super(SolutionStream, self).__init__()
    self._address = address
    self._stream = solutions.subject.map(self._on_solution_stream)
    # Route events from self._stream back into and out of ourselves.
    self._stream.subscribe(self)

  def _on_solution_stream(self, e):
    return (self._address, e)

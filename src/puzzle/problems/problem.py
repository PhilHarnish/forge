class Problem(object):
  def __init__(self, name, lines):
    self.name = name
    self.lines = lines

    self._solutions = None

  def solutions(self):
    if self._solutions is None:
      self._solutions = self._solve()
    return self._solutions

  def _solve(self):
    raise NotImplementedError()

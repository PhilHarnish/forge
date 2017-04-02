import collections


class Problem(object):
  def __init__(self, name, lines):
    self.name = name
    self.lines = lines
    self._solutions = None
    self._constraints = []

  def constrain(self, fn):
    self._constraints.append(fn)
    # Invalidate solutions.
    self._solutions = None

  def solutions(self):
    if self._solutions is None:
      self._solutions = collections.OrderedDict(
          (k, v) for k, v in self._solve().items() if all(
              [fn(k, v) for fn in self._constraints]
          )
      )
    return self._solutions

  def _solve(self):
    """Solves Problem.

    Returns:
      dict Dict mapping solution to score.
    """
    raise NotImplementedError()

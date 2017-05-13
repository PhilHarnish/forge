from data import meta


class Problem(object):
  def __init__(self, name, lines):
    self.name = name
    self.lines = lines
    self._solutions = None
    self._constraints = []

  @property
  def kind(self):
    return str(type(self)).strip("'<>").split('.').pop()

  @property
  def solution(self):
    return self.solutions().peek()

  def constrain(self, fn):
    self._constraints.append(fn)
    # Invalidate solutions.
    self._solutions = None

  def solutions(self):
    if self._solutions is None:
      self._solutions = meta.Meta(
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

  def __repr__(self):
    return '%s()' % self.__class__.__name__

import collections

from data import meta

_THRESHOLD = 0.01


class Problem(object):
  def __init__(self, name, lines, threshold=_THRESHOLD):
    self.name = name
    self.lines = lines
    self._threshold = threshold
    self._solutions = None
    self._notes = collections.defaultdict(list)
    self._constraints = [
      lambda k, v: v > self._threshold
    ]

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
    self._solutions_iter = None

  def solutions(self):
    if self._solutions is None:
      self._solutions_iter = self._solve_iter()
      results = []
      for k, v in self._solutions_iter:
        if all(fn(k, v) for fn in self._constraints):
          results.append((k, v))
      self._solutions = meta.Meta(results)
    return self._solutions

  def notes_for(self, solution):
    return self._notes.get(solution, [])

  def _solve_iter(self):
    return iter(self._solve().items())

  def _solve(self):
    """Solves Problem.

    Returns:
      dict Dict mapping solution to score.
    """
    raise NotImplementedError()

  def __repr__(self):
    return '%s()' % self.__class__.__name__

import rx

from data import meta
from data import stream
from puzzle.heuristics import analyze

class Puzzle(object):
  def __init__(self, source):
    self._meta_problems = []
    if isinstance(source, str):
      lines = [line for line in source.split('\n') if line]
    elif isinstance(source, list):
      lines = source
    elif isinstance(source, Puzzle):
      lines = source.solutions()
    else:
      raise NotImplementedError(
          'Puzzle source type %s unsupported' % type(source))
    for i, (meta_problem, consumed) in enumerate(
        analyze.identify_problems(lines)):
      self._meta_problems.append(_reify(meta_problem, '#%s' % i, consumed))
    self._observable = stream.Stream()

  def problem(self, index):
    return self._meta_problems[index]

  def problems(self):
    return [p.active for p in self._meta_problems]

  def solutions(self):
    return [p.solution for p in self._meta_problems]

  def subscribe(self, observer):
    self._observable.subscribe(observer)

  def get_next_stage(self):
    return Puzzle(self)


def _reify(meta_problem, name, lines):
  result = _MetaProblem()
  for value, weight in meta_problem.items():
    result[value(name, lines)] = weight
  return result


class _MetaProblem(meta.Meta):
  # Sentinel value for 'no solution found'.
  _NO_SOLUTION = {}

  def __init__(self):
    super(_MetaProblem, self).__init__()
    self._active = None
    self._solution = self._NO_SOLUTION
    self._observable = stream.Stream()

  @property
  def active(self):
    return self._active or self.peek()

  @property
  def solution(self):
    if self._solution is self._NO_SOLUTION:
      return self.active.solutions().peek()
    return self._solution

  @solution.setter
  def solution(self, value):
    if self._solution == value:
      return
    self._solution = value
    self._observable.publish_value(self)

  def subscribe(self, observer):
    self._observable.subscribe(observer)
    observer.on_next(self)

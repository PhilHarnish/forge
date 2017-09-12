from rx import subjects

from data import observable_meta
from puzzle.heuristics import analyze
from puzzle.puzzlepedia import solution_stream


class Puzzle(subjects.Subject):
  def __init__(self, name, source, hint=None, **kwargs):
    super(Puzzle, self).__init__()
    self._meta_problems = []
    self._child_streams = []
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
        analyze.identify_problems(lines, hint=hint)):
      problem = _reify(meta_problem, '#%s' % i, consumed, **kwargs)
      self._meta_problems.append(problem)
      self._child_streams.append(solution_stream.SolutionStream(
          str(i), problem))
    self._observable = solution_stream.SolutionStream(
        name, observable_meta.ObservableMeta(), self._child_streams)
    self._observable.subscribe(self)

  def problem(self, index):
    return self._meta_problems[index]

  def problems(self):
    return [p.active for p in self._meta_problems]

  def solutions(self):
    return [p.solution for p in self._meta_problems]

  def get_next_stage(self):
    return Puzzle('meta', self)


def _reify(meta_problem, name, lines, **kwargs):
  result = _MetaProblem()
  for value, weight in meta_problem.items():
    result[value(name, lines, **kwargs)] = weight
  return result


class _MetaProblem(observable_meta.ObservableMeta):
  # Sentinel value for 'no solution found'.
  _NO_SOLUTION = {}

  def __init__(self):
    super(_MetaProblem, self).__init__()
    self._active = None
    self._solution = self._NO_SOLUTION

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
    self._changed()

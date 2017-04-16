from src.data import meta
from src.puzzle.heuristics import analyze

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
    for i, (meta_problem, consumed) in enumerate(analyze.identify_lines(lines)):
      self._meta_problems.append(_reify(meta_problem, '#%s' % i, consumed))

  def problems(self):
    return [p.active for p in self._meta_problems]

  def solutions(self):
    return [p.active.solution for p in self._meta_problems]

  def get_next_stage(self):
    return Puzzle(self)


def _reify(meta_problem, name, lines):
  result = _MetaProblem()
  for value, weight in meta_problem.items():
    result[value(name, lines)] = weight
  return result


class _MetaProblem(meta.Meta):
  _active = None

  @property
  def active(self):
    return self._active or self.peek()

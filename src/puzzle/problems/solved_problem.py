import re

from puzzle.problems import problem

_SOLVED_REGEX = re.compile(r'^([A-Z\s]+)\s+\((.*)\)$')


class SolvedProblem(problem.Problem):
  def __init__(self, name, lines, *args, **kwargs):
    if len(lines) > 1:
      raise ValueError('Only one line per SolvedProblem')
    # Remove solution from line.
    self._solution, line = _parse(lines[0])
    lines = [line]
    super(SolvedProblem, self).__init__(name, lines, *args, **kwargs)

  @staticmethod
  def score(lines):
    if len(lines) > 1:
      return 0
    match = _SOLVED_REGEX.match(lines[0])
    if not match:
      return 0
    return 1

  def _solve_iter(self):
    yield self._solution, 1

def _parse(src):
  match = _SOLVED_REGEX.match(src)
  return match.group(1), match.group(2)

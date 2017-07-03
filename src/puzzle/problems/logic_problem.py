import ast
import sys

from puzzle.problems import problem


class LogicProblem(problem.Problem):
  def __init__(self, name, lines):
    super(LogicProblem, self).__init__(name, lines)
    program = '\n'.join(lines)
    self._parsed = self._parse(program)

  @staticmethod
  def score(lines):
    if len(lines) <= 1:
      return 0
    program = '\n'.join(lines)
    try:
      parsed = ast.parse(program)
      if isinstance(parsed, ast.Module):
        return min(1, len(parsed.body) / 10)
    except:
      return 0
    return sys.float_info.epsilon

  def _parse(self, program):
    parsed = ast.parse(program)
    if isinstance(parsed, ast.Module):
      return parsed.body
    raise TypeError('Program did not parse:\n%s' % program)

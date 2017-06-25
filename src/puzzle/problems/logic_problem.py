import ast
import sys

from puzzle.problems import problem


class LogicProblem(problem.Problem):
  @staticmethod
  def score(lines):
    if len(lines) <= 1:
      return 0
    program = '\n'.join(lines)
    try:
      ast.parse(program)
    except:
      return 0
    return sys.float_info.epsilon
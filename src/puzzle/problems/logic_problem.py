import ast
import sys

from data.logic import _grammar_transformer
from puzzle.problems import problem


class LogicProblem(problem.Problem):
  @staticmethod
  def score(lines):
    if len(lines) <= 1:
      return 0
    program = '\n'.join(lines)
    try:
      parsed = ast.parse(program)
      if isinstance(parsed, ast.Module):
        n_lines = sum(line.startswith('#') for line in lines) + len(parsed.body)
        return min(1, n_lines / 10)
    except:
      return 0
    return sys.float_info.epsilon

  def _solve_iter(self):
    model = _model(self.lines)
    solver = _solver(model)
    while solver.solve():
      yield str(solver), 1


def _parse(lines):
  return _grammar_transformer.transform('\n'.join(lines))


def _model(lines):
  parsed = _parse(lines)
  compiled = compile(parsed, '<string>', 'exec')
  variables = {}
  exec(compiled, variables)
  return variables['model']


def _solver(model):
  return model.load('Mistral')

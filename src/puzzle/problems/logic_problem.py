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

  def _parse(self):
    return _grammar_transformer.transform('\n'.join(self.lines))

  def _solve_iter(self):
    parsed = self._parse()
    compiled = compile(parsed, '<string>', 'exec')
    variables = {}
    exec(compiled, variables)
    model = variables['model']
    solver = model.load('Mistral')
    while solver.solve():
      yield str(solver), 1

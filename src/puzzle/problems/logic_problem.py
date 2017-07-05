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
        return min(1, len(parsed.body) / 10)
    except:
      return 0
    return sys.float_info.epsilon

  def _parse(self):
    return _grammar_transformer.transform('\n'.join(self.lines))

  def _solve(self):
    parsed = self._parse()
    compiled = compile(parsed, '<string>', 'exec')
    variables = {}
    exec(compiled, variables)
    model = variables['model']
    solver = model.load('Mistral')
    solver.solve()
    if not solver.solved():
      return {}
    solutions = {}
    solutions[str(solver)] = 1
    return solutions

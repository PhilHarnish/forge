import ast
import sys

from data.logic import _grammar_transformer
from puzzle.problems import problem

# These are specific enough to rarely appear.
_CONCLUSIVE_TOP_LEVEL_NODES = (
  ast.For,  # for x in y:.
  ast.FunctionDef,  # def foo():.
  ast.If,  # If statements.
)
# These are less conclusive.
_INTERESTING_TOP_LEVEL_NODES = (
  ast.Assign,
)
_INTERESTING_TOP_LEVEL_EXPRESSIONS = (
  ast.BinOp,  # a | b.
  ast.Compare,  # Dimensions, X <= Y.
)


_SOLUTION_LIMIT = 3  # Solutions should be unique, after all.


class LogicProblem(problem.Problem):
  @staticmethod
  def score(lines):
    if len(lines) <= 1:
      return 0
    program = '\n'.join(lines)
    try:
      parsed = ast.parse(program)
      if isinstance(parsed, ast.Module):
        return min(1, _program_interesting_ratio(parsed) * 1.25)
    except SyntaxError:
      return 0
    return sys.float_info.epsilon

  def _solve_iter(self):
    model = _model(self.lines)
    seen = set()
    solvers = ['Mistral', 'MiniSat']
    while not seen and solvers:
      solver = _solver(model, solvers.pop(0))
      while solver.solve():
        if len(seen) >= _SOLUTION_LIMIT:
          break
        solution = str(solver)
        if solution in seen:
          # FIXME: No idea why this happens with some compacted problems.
          # Finding out why would be exhausting.
          continue
        seen.add(solution)
        yield str(solver), 1


def _parse(lines):
  return _grammar_transformer.transform('\n'.join(lines))


def _model(lines):
  parsed = _parse(lines)
  compiled = compile(parsed, '<string>', 'exec')
  variables = {}
  exec(compiled, variables)
  return variables['model']


def _solver(model, engine):
  return model.load(engine)


def _program_interesting_ratio(module):
  interesting = 0
  for node in module.body:
    if isinstance(node, _CONCLUSIVE_TOP_LEVEL_NODES):
      return 1
    elif isinstance(node, _INTERESTING_TOP_LEVEL_NODES):
      interesting +=1
    elif not isinstance(node, ast.Expr):
      continue
    elif isinstance(node.value, _INTERESTING_TOP_LEVEL_EXPRESSIONS):
      interesting += 1
  return interesting / len(module.body)

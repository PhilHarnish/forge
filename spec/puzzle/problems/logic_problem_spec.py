import ast

from puzzle.problems import logic_problem
from spec.mamba import *

with description('LogicProblem score'):
  with it('ignores empty input'):
    expect(logic_problem.LogicProblem.score([''])).to(equal(0))

  with it('rejects a single line'):
    expect(logic_problem.LogicProblem.score(['a single line'])).to(equal(0))

  with it('assigns a non-zero score to many lines'):
    expect(logic_problem.LogicProblem.score([
      'this', 'has', 'many', 'lines',
    ])).to(be_above(0))

with description('LogicProblem constructor'):
  with it('parses empty input'):
    problem = logic_problem.LogicProblem('test', [''])
    expect(problem._parse()).to(be_a(ast.Module))

  with it('parses comments'):
    problem = logic_problem.LogicProblem('test', [
      '# This is a comment.'
    ])
    expect(problem._parse()).to(be_a(ast.Module))

  with it('parses statements'):
    problem = logic_problem.LogicProblem('test', [
      '# This is a comment.',
      'ages <= {10, 11, 12}'
    ])
    expect(problem._parse()).to(be_a(ast.Module))

with description('LogicProblem solutions'):
  with it('finds multiple solutions'):
    program = """
      name <= {Andy, Bob}
      age <= {10, 11}
    """
    problem = logic_problem.LogicProblem('test', program.split('\n'))
    expected = set(textwrap.dedent(txt.strip('\n')) for txt in [
        """
          name | age
          Andy |  11
           Bob |  10
        """,
        """
          name | age
          Andy |  10
           Bob |  11
        """,
    ])
    expect(set(problem.solutions().keys())).to(equal(expected))

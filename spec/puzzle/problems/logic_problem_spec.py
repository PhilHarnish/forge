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

with description('LogicProblem parsing'):
  with it('parses empty input'):
    lines = ['']
    expect(logic_problem._parse(lines)).to(be_a(ast.Module))

  with it('parses comments'):
    lines = [
      '# This is a comment.'
    ]
    expect(logic_problem._parse(lines)).to(be_a(ast.Module))

  with it('parses statements'):
    lines = [
      '# This is a comment.',
      'ages <= {10, 11, 12}'
    ]
    expect(logic_problem._parse(lines)).to(be_a(ast.Module))

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

  with it('finds multiple solutions'):
    program = """
      name <= {Andy, Bob, Cynthia}
      age <= {10, 10, 11}
    """
    problem = logic_problem.LogicProblem('test', program.split('\n'))
    expected = set(textwrap.dedent(txt.strip('\n')) for txt in [
        """
            name | age
            Andy |  10
             Bob |  10
         Cynthia |  11
        """,
        """
            name | age
            Andy |  10
             Bob |  11
         Cynthia |  10
        """,
        """
            name | age
            Andy |  11
             Bob |  10
         Cynthia |  10
        """,
    ])
    expect(set(problem.solutions().keys())).to(equal(expected))

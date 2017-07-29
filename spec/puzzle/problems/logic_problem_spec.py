import ast

import astor

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

  with it('solves simple problems'):
    program = """
      name <= {Andy, Bob, Cathy}
      occupation <= {CEO, ProjectManager, Analyst}
      age <= {10, 11, 12}
      # The CEO is not the youngest.
      CEO.age > ProjectManager.age
      CEO.age > Analyst.age
      # Andy is a year younger than Bob.
      Andy.age + 1 == Bob.age
      # Cathy is older than the Project Manager.
      Cathy.age > ProjectManager.age
      # Bob is either the CEO or the Project Manager.
      Bob == CEO or Bob == ProjectManager
    """
    problem = logic_problem.LogicProblem('test', program.split('\n'))
    parsed = logic_problem._parse(program.split('\n'))
    expect(astor.to_source(parsed)).to(look_like('''
      from data.logic.dsl import *
      dimensions = DimensionFactory()
      model = Model(dimensions)
      andy, bob, cathy = name = dimensions(name=['Andy', 'Bob', 'Cathy'])
      ceo, projectmanager, analyst = occupation = dimensions(occupation=['CEO',
          'ProjectManager', 'Analyst'])
      _10, _11, _12 = age = dimensions(age=[10, 11, 12])
      """# The CEO is not the youngest."""
      model(ceo.age > projectmanager.age)
      model(ceo.age > analyst.age)
      """# Andy is a year younger than Bob."""
      model(andy.age + 1 == bob.age)
      """# Cathy is older than the Project Manager."""
      model(cathy.age > projectmanager.age)
      """# Bob is either the CEO or the Project Manager."""
      model((bob == ceo) ^ (bob == projectmanager))
    '''))
    model = logic_problem._model(program.split('\n'))
    expect(str(model)).to(look_like("""
      assign:
        occupation["CEO"].age[None] in {10..12}
        occupation["ProjectManager"].age[None] in {10..12}
        occupation["Analyst"].age[None] in {10..12}
        name["Bob"].age[None] in {10..12}
        name["Andy"].age[None] in {10..12}
        name["Cathy"].age[None] in {10..12}
        name["Bob"].occupation["CEO"] in {0,1}
        name["Bob"].occupation["ProjectManager"] in {0,1}

      subject to:
        (occupation["CEO"].age[None] > occupation["ProjectManager"].age[None])
        (occupation["CEO"].age[None] > occupation["Analyst"].age[None])
        (name["Bob"].age[None] == (name["Andy"].age[None] + 1))
        (name["Cathy"].age[None] > occupation["ProjectManager"].age[None])
        ((name["Bob"].occupation["CEO"] + name["Bob"].occupation["ProjectManager"]) == 1)
    """))
    expect(problem.solution).to(look_like("""
       name |     occupation | age
       Andy |        Analyst |  10
        Bob | ProjectManager |  11
      Cathy |            CEO |  12
    """))
    expect(problem.solutions()).to(have_len(1))

import astor

from data import warehouse
from puzzle.examples.mim import p3_1
from puzzle.problems import logic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('p3_1'):
  with before.all:
    warehouse.save()
    prod_config.init()
    self.puzzle = p3_1.get()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with description('solution'):
    with it('scores the source as a LogicProblem'):
      expect(logic_problem.LogicProblem.score(
          p3_1.SOURCE.split('\n'))).to(equal(1))

    with it('identifies puzzle type'):
      problems = self.puzzle.problems()
      expect(problems).to(have_len(1))
      problem = problems[0]
      expect(problem).to(be_a(logic_problem.LogicProblem))

    with _it('parses puzzle'):
      node = logic_problem._parse(p3_1.SOURCE.split('\n'))
      print(astor.to_source(node))

    with _it('models puzzle'):
      model = logic_problem._model(p3_1.SOURCE.split('\n'))
      model.add(model.dimension_constraints())
      print(str(model))

    with it('exports a solution'):
      problem = self.puzzle.problems()[0]
      expect(problem.solution).to(look_like(p3_1.SOLUTION))

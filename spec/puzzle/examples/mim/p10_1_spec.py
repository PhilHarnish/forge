import astor

from data import warehouse
from puzzle.examples.mim import p10_1
from puzzle.problems import logic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('p10_1'):
  with before.all:
    warehouse.save()
    prod_config.init()
    self.puzzle = p10_1.get()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with description('solution'):
    with it('scores the source as a LogicProblem'):
      expect(logic_problem.LogicProblem.score(
          p10_1.SOURCE.split('\n'))).to(equal(1))

    with it('identifies puzzle type'):
      problems = self.puzzle.problems()
      expect(problems).to(have_len(1))
      problem = problems[0]
      expect(problem).to(be_a(logic_problem.LogicProblem))

    with it('parses puzzle'):
      node = logic_problem._parse(p10_1.SOURCE.split('\n'))
      print(astor.to_source(node))

    with it('models puzzle'):
      model = logic_problem._model(p10_1.SOURCE.split('\n'))
      print(str(model))

    with it('exports a solution'):
      problem = self.puzzle.problems()[0]
      with breakpoints:
        expect(problem.solution).to(look_like(p10_1.SOLUTION))

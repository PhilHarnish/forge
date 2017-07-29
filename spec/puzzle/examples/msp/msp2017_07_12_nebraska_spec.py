import astor

from data import warehouse
from puzzle.examples.msp import msp2017_07_12_nebraska
from puzzle.problems import logic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('msp2017_07_12_nebraska'):
  with before.all:
    warehouse.save()
    prod_config.init()
    self.puzzle = msp2017_07_12_nebraska.get()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with description('solution'):
    with it('scores the source as a LogicProblem'):
      expect(logic_problem.LogicProblem.score(
          msp2017_07_12_nebraska.SOURCE.split('\n'))).to(equal(1))

    with it('identifies puzzle type'):
      problems = self.puzzle.problems()
      expect(problems).to(have_len(1))
      problem = problems[0]
      expect(problem).to(be_a(logic_problem.LogicProblem))

    with _it('parses puzzle'):
      parsed = logic_problem._parse(msp2017_07_12_nebraska.SOURCE.split('\n'))
      print(astor.to_source(parsed))

    with _it('models puzzle'):
      model = logic_problem._model(msp2017_07_12_nebraska.SOURCE.split('\n'))
      model.add(model.dimension_constraints())
      print(str(model))

    with it('exports a solution'):
      problem = self.puzzle.problems()[0]
      expect(problem.solution).to(look_like(
          msp2017_07_12_nebraska.SOLUTION))

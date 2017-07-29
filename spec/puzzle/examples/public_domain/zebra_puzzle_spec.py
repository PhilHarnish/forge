import astor

from data import warehouse
from puzzle.examples.public_domain import zebra_puzzle
from puzzle.problems import logic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('zebra_puzzle'):
  with description('solution'):
    with before.all:
      warehouse.save()
      prod_config.init()
      self.subject = zebra_puzzle.get()

    with after.all:
      prod_config.reset()
      warehouse.restore()

    with it('identifies puzzle type'):
      problems = self.subject.problems()
      expect(problems).to(have_len(1))
      problem = problems[0]
      expect(problem).to(be_a(logic_problem.LogicProblem))

    with it('parses expressions'):
      parsed = logic_problem._parse(zebra_puzzle.SOURCE.split('\n'))
      expect(astor.to_source(parsed)).to(look_like(zebra_puzzle.PARSED))

    with it('models puzzle'):
      model = logic_problem._model(zebra_puzzle.SOURCE.split('\n'))
      print(str(model))

    with it('exports a solution'):
      problem = self.subject.problems()[0]
      expect(problem.solution).to(look_like(zebra_puzzle.SOLUTION))

import astor

from data import warehouse
from puzzle.examples.public_domain import zebra_puzzle
from puzzle.problems import logic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with description('zebra_puzzle'):
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
      problem = self.subject.problems()[0]
      expect(astor.to_source(problem._parse())).to(
          look_like(zebra_puzzle.PARSED))

    with it('exports a model'):
      problem = self.subject.problems()[0]
      # TODO: This is incorrect.
      expect(problem._solve()).to(equal((
        ['position', 'color', 'animal', 'cigarette', 'drink', 'nationality'],
        [
          [[1], ['Green'], ['Zebra'], ['Chesterfields'], ['Coffee'],
            ['Norwegian']],
          [[2], ['Blue'], ['Fox'], ['Parliaments'], ['Water'], ['Japanese']],
          [[3], ['Yellow'], ['Dog'], ['Kools'], ['Milk'], ['Spaniard']],
          [[4], ['Red'], ['Horse'], ['Lucky Strike'], ['Orange Juice'],
            ['Englishman']],
          [[5], ['Ivory'], ['Snails'], ['Old Gold'], ['Tea'], ['Ukrainian']]
        ]
      )))

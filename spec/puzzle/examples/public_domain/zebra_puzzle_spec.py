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
      problem = self.subject.problems()[0]
      expect(astor.to_source(problem._parse())).to(
          look_like(zebra_puzzle.PARSED))

    with it('exports a model'):
      problem = self.subject.problems()[0]
      expect(problem.solution).to(look_like("""
      position |  color | animal |     cigarette |        drink | nationality
             1 | Yellow |    Fox |         Kools |        Water |   Norwegian
             2 |   Blue |  Horse | Chesterfields |          Tea |   Ukrainian
             3 |    Red | Snails |      Old Gold |         Milk |  Englishman
             4 |  Ivory |    Dog |  Lucky Strike | Orange Juice |    Spaniard
             5 |  Green |  Zebra |   Parliaments |       Coffee |    Japanese
      """))

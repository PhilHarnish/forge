import astor

from data import warehouse
from puzzle.examples.gph import very_fun_logic_puzzle
from puzzle.problems import logic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with description('very_fun_logic_puzzle'):
  with before.all:
    warehouse.save()
    prod_config.init()
    self.houses = very_fun_logic_puzzle.get_houses()
    self.roses = very_fun_logic_puzzle.get_roses()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with description('house solution'):
    with it('scores the source as a LogicProblem'):
      expect(logic_problem.LogicProblem.score(
          very_fun_logic_puzzle.HOUSE_SOURCE.split('\n'))).to(equal(1))

    with it('identifies puzzle type'):
      problems = self.houses.problems()
      expect(problems).to(have_len(1))
      problem = problems[0]
      expect(problem).to(be_a(logic_problem.LogicProblem))

    with it('parses expressions'):
      expect(astor.to_source(logic_problem._parse(
          very_fun_logic_puzzle.HOUSE_SOURCE.split('\n')))
      ).to(look_like(very_fun_logic_puzzle.HOUSE_PARSED))

    with it('exports a solution'):
      problem = self.houses.problems()[0]
      expect(problem.solution).to(look_like(
          very_fun_logic_puzzle.HOUSE_SOLUTION))

  with description('rose solution'):
    with it('scores the source as a LogicProblem'):
      expect(logic_problem.LogicProblem.score(
          very_fun_logic_puzzle.ROSE_SOURCE.split('\n'))).to(equal(1))

    with it('identifies puzzle type'):
      problems = self.roses.problems()
      expect(problems).to(have_len(1))
      problem = problems[0]
      expect(problem).to(be_a(logic_problem.LogicProblem))

    with it('parses expressions'):
      expect(astor.to_source(logic_problem._parse(
          very_fun_logic_puzzle.ROSE_SOURCE.split('\n')))
      ).to(look_like(very_fun_logic_puzzle.ROSE_PARSED))

    with it('exports a solution'):
      problem = self.roses.problems()[0]
      expect(problem.solution).to(look_like(
          very_fun_logic_puzzle.ROSE_SOLUTION))

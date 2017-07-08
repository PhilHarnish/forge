import astor

from data import warehouse
from puzzle.examples.gph import very_fun_logic_puzzle
from puzzle.problems import logic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('very_fun_logic_puzzle'):
  with description('solution'):
    with before.all:
      warehouse.save()
      prod_config.init()
      self.subject = very_fun_logic_puzzle.get()

    with after.all:
      prod_config.reset()
      warehouse.restore()

    with it('scores the source as a LogicProblem'):
      expect(logic_problem.LogicProblem.score(
          very_fun_logic_puzzle.SOURCE.split('\n'))).to(equal(1))

    with it('identifies puzzle type'):
      problems = self.subject.problems()
      expect(problems).to(have_len(1))
      problem = problems[0]
      expect(problem).to(be_a(logic_problem.LogicProblem))

    with it('parses expressions'):
      problem = self.subject.problems()[0]
      expect(astor.to_source(problem._parse())).to(
          look_like(very_fun_logic_puzzle.PARSED))

    with it('exports a solution'):
      problem = self.subject.problems()[0]
      expect(problem.solution).to(look_like(very_fun_logic_puzzle.SOLUTION))

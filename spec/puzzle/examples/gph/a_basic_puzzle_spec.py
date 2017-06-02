from data import warehouse
from puzzle.examples.gph import a_basic_puzzle
from puzzle.problems import number_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('a_basic_puzzle'):
  with before.all:
    warehouse.save()
    prod_config.init()
    self.subject = a_basic_puzzle.get()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('parses'):
    problems = self.subject.problems()
    expect(problems).to(have_len(len(a_basic_puzzle.SOURCE.split('\n')) - 2))
    for problem in problems:
      expect(problem).to(be_a(number_problem.NumberProblem))

  with it('solves first problem'):
    expect(self.subject.problem(0).solution).not_to(be_empty)

  with it('gets some solutions right'):
    solutions = self.subject.solutions()
    expect(solutions).to(equal([
      'decimal +25',
      'octal +12',
      None,  # 'sept e nary +1' lost when Trie threshold was changed.
      'binary +1',
      None,
      None,  # 'qui nary +9' lost when Trie threshold was changed.
      None,
      None,
      'quaternary +12',
      None
    ]))

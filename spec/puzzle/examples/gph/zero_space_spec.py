from data import warehouse
from puzzle.examples.gph import zero_space
from puzzle.problems.crossword import crossword_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('zero_space'):
  with before.all:
    warehouse.save()
    prod_config.init()
    self.subject = zero_space.get()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('parses'):
    problems = self.subject.problems()
    expect(problems).to(have_len(len(zero_space.SOLUTIONS)))
    for problem in problems:
      expect(problem).to(be_a(crossword_problem.CrosswordProblem))

  with it('gets some solutions right'):
    solutions = self.subject.solutions()
    expect(solutions).to(equal([
      None,
      None,
      None,
      None,
      'cnote',
      None,
      None,
      None,
      None,
      None,
      'probono',
      None,
      'hikes',  # Wrong.
      'neath',  # Wrong.
      None,
      'romero',  # Wrong.
      'enolagay',
      'fitin',
      'ores',  # Wrong.
      'alas',
      'idle',
      None,
      'gear',
      None,
      None,
      'spews'
    ]))

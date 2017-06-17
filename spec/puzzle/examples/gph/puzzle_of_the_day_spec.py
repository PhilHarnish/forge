from data import warehouse
from puzzle.examples.gph import puzzle_of_the_day
from puzzle.problems.crossword import crossword_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('puzzle_of_the_day'):
  with before.all:
    warehouse.save()
    prod_config.init()
    self.subject = puzzle_of_the_day.get()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('parses'):
    problems = self.subject.problems()
    expect(problems).to(have_len(len(puzzle_of_the_day.SOLUTIONS)))
    for problem in problems:
      expect(problem).to(be_a(crossword_problem.CrosswordProblem))

  with it('solves first problem'):
    expect(self.subject.problem(0).solution).not_to(be_empty)

  with it('gets some solutions right'):
    solutions = self.subject.solutions()
    expect(solutions).to(equal([
      'pacino',  # Wrong.
      'nitpick',
      None,
      'windpipe',
      None,
      'laboroflove',  # Wrong.
      None,
      None,
      'pilaf',
      'tribal',  # Wrong.
      None,
      'carrera',  # Wrong.
      None,
      None,
      None,
      None,
      None,
      'tacky',  # Wrong.
      None,
    ]))

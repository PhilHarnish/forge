from data import warehouse
from puzzle.examples.gph import puzzle_of_the_day
from puzzle.problems import crossword_problem
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
    matches = []
    for i, (left, right) in enumerate(
        zip(solutions, puzzle_of_the_day.SOLUTIONS)):
      if left and right and left.lower() == right.lower():
        matches.append('%s: %s' % (i + 1, left))
    expect(matches).to(equal([
      '2: nitpick',
      '4: windpipe',
      '9: pilaf',
    ]))

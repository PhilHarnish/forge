from data import warehouse
from puzzle.examples.gph import a_glistening_occasion
from puzzle.problems import acrostic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('a_glistening_occasion'):
  with before.all:
    warehouse.save()
    prod_config.init()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with description('initial solution'):
    with before.each:
      self.subject = a_glistening_occasion.get(correct=False)

    with it('parses'):
      problems = self.subject.problems()
      expect(problems).to(have_len(1))
      for problem in problems:
        expect(problem).to(be_a(acrostic_problem.AcrosticProblem))

    with it('gets a hit even with one unknown'):
      solutions = self.subject.solutions()
      expect(solutions).to(equal(['scoreboard']))

  with description('correct solution'):
    with before.each:
      self.subject = a_glistening_occasion.get(correct=True)

    with it('parses'):
      problems = self.subject.problems()
      expect(problems).to(have_len(1))
      for problem in problems:
        expect(problem).to(be_a(acrostic_problem.AcrosticProblem))

    with it('gets a hit'):
      solutions = self.subject.solutions()
      expect(solutions).to(equal(['scoreboard']))

from expects import *

from src.puzzle.problems import problem

with description('Problem'):
  with it('instantiates'):
    expect(problem.Problem('example', [''])).not_to(be_none)

with description('register'):
  with after.each:
    problem.unregister_all()

  with it('registers types'):
    class Example(object):
      pass
    problem.register(Example)
    expect(problem.problem_types()).to(equal({Example}))

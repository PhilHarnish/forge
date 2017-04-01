from expects import *

from src.puzzle.problems import problem

with description('Problem'):
  with it('instantiates'):
    expect(problem.Problem('example', [''])).not_to(be_none)

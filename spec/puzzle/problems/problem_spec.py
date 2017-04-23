from spec.mamba import *
from unittest import mock

from puzzle.problems import problem

with description('Problem'):
  with it('instantiates'):
    expect(problem.Problem('example', [''])).not_to(be_none)

  with it('caches solutions'):
    class ExampleProblem(problem.Problem):
      _solve = mock.Mock(return_value={'solution': 1})
    ex = ExampleProblem('example', [])
    expect(ex.solutions()).to(equal({'solution': 1}))
    expect(ex._solve.call_count).to(equal(1))
    ex.solutions()
    expect(ex._solve.call_count).to(equal(1))

  with it('constrains solutions'):
    class ExampleProblem(problem.Problem):
      _solve = mock.Mock(return_value={
        'solution 1': 1,
        'solution 2': .5,
      })
    ex = ExampleProblem('example', [])
    ex.constrain(lambda k, v: v >= 1)
    expect(ex.solutions()).to(equal({'solution 1': 1}))

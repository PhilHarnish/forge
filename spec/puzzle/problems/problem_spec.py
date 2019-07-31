from puzzle.problems import problem
from spec.mamba import *

with description('Problem'):
  with it('instantiates'):
    expect(problem.Problem('example', [''])).not_to(be_none)

  with it('strs itself'):
    src = ['a', 'b', 'c']
    expect(str(problem.Problem('example', src))).to(look_like("""
      a
      b
      c
    """))

  with it('reprs itself'):
    expect(repr(problem.Problem('example', ['src']))).to(look_like("""
      Problem('example', ['src'])
    """))

  with it('stores notes for solutions'):
    class ExampleProblem(problem.Problem):
      _solve = mock.Mock(return_value={
        'solution 1': 1,
        'solution 2': .5,
      })


    ex = ExampleProblem('example', [])
    for solution in ex.solutions():
      expect(ex.notes_for(solution)).to(be_a(list))

from puzzle.constraints import solution_constraints
from puzzle.problems import problem
from spec.mamba import *


class ExampleProblem(problem.Problem):
  _solve = mock.Mock(return_value={
    'solution 1': 1,
    'solution 2': .5,
  })

  def constraints(self) -> solution_constraints.SolutionConstraints:
    return self._solution_constraints


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
    ex = ExampleProblem('example', [])
    for solution in ex.solutions():
      expect(ex.notes_for(solution)).to(be_a(list))

  with it('forwards events from solution constraints'):
    ex = ExampleProblem('example', [])
    on_solutions_change_stub = mock.Mock()
    ex.subscribe(on_solutions_change_stub)
    ex.constraints().weight_threshold = 0.5
    expect(on_solutions_change_stub.on_next).to(have_been_called_once)

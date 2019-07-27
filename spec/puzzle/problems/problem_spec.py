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

  with it('stores notes for solutions'):
    class ExampleProblem(problem.Problem):
      _solve = mock.Mock(return_value={
        'solution 1': 1,
        'solution 2': .5,
      })


    ex = ExampleProblem('example', [])
    for solution in ex.solutions():
      expect(ex.notes_for(solution)).to(be_a(list))

  with description('iterative solving'):
    with before.each:
      results = [
        ('first value', 0.9),
        ('better value', 1.0),
        ('bad value', 0.5),
      ]
      self.pos = 0
      def solve_iter_source() -> problem.Solutions:
        while self.pos < len(results):
          yield results[self.pos]
          self.pos += 1
      solve_iter_stub = mock.Mock(return_value=solve_iter_source())
      class ExampleProblem(problem.Problem):
        _solve_iter = solve_iter_stub

      self.solve_iter_stub = solve_iter_stub
      self.subject = ExampleProblem('example', [])

    with it('solutions() returns all results'):
      expect(list(self.subject.solutions().items())).to(equal([
        ('better value', 1.0),
        ('first value', 0.9),
        ('bad value', 0.5),
      ]))

    with it('solutions() only calls _solve_iter once'):
      expect(self.solve_iter_stub).not_to(have_been_called)
      self.subject.solutions()
      expect(self.solve_iter_stub).to(have_been_called_once)
      self.subject.solutions()
      expect(self.solve_iter_stub).to(have_been_called_once)

    with it('solutions() only calls _solve_iter once, even if reconstrained'):
      expect(self.subject.solutions()).to(have_len(3))
      self.subject.constrain(lambda solution, weight: weight > 0.5)
      expect(list(self.subject.solutions().items())).to(equal([
        ('better value', 1.0),
        ('first value', 0.9),
      ]))
      expect(self.solve_iter_stub).to(have_been_called_once)

    with it('solutions stream via yield'):
      expect(self.pos).to(equal(0))
      for i, s in enumerate(self.subject):
        expect(self.pos).to(equal(i))

from data.logic import _solver
from spec.mamba import *

with description('_solver'):
  with before.each:
    self.solutions = ([], [])
    self.solver = mock.Mock()
    self.subject = _solver.Solver(
        mock.Mock(
            get_solutions=lambda: self.solutions,
        ),
        solver=self.solver,
        deferred=[],
    )

  with it('calls solve only once'):
    expect(self.solver).not_to(have_been_called)
    self.subject.solve()
    expect(self.solver.solve).to(have_been_called)
    self.subject.solve()
    expect(self.solver.solve).to(have_been_called_once)

  with it('prints nothing until solved'):
    expect(str(self.subject)).to(equal('<unsolved>'))

  with it('prints nothing interesting if solutions are empty'):
    self.subject.solve()
    expect(str(self.subject)).to(look_like(''))

  with it('prints solutions'):
    self.solutions = (
        ['header1', 'header2'],
        [
          [['value1'], ['value2']],
        ],
    )
    self.subject.solve()
    expect(str(self.subject)).to(look_like("""
      header1 | header2
       value1 |  value2
    """))

  with it('prints with inconsistent widths'):
    self.solutions = (
        ['header', 'wide header'],
        [
          [['value'], [1, 2, 3, 4, 5]],
        ],
    )
    self.subject.solve()
    expect(str(self.subject)).to(look_like("""
      header |   wide header
       value | 1, 2, 3, 4, 5
    """))

  with it('queues functions to run after each solution'):
    deferred = mock.Mock()
    self.subject._deferred.append(deferred)
    self.subject.solve()
    expect(deferred).to(have_been_called)

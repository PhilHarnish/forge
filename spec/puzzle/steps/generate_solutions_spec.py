import collections

from puzzle.constraints import solution_constraints
from puzzle.steps import generate_solutions
from spec.mamba import *

_SOLUTIONS = collections.OrderedDict((
  ('early_low', 0.1),
  ('early_high', 1.0),
  ('after_early_high', 0.9),
  ('mid_low', 0.2),
  ('late_mid', 0.5),
  ('late_low', 0.3),
  ('late_high', 0.8),
))
def _source() -> generate_solutions.Solutions:
  yield from _SOLUTIONS.items()


with description('generate_solutions') as self:
  with before.each:
    self.constraints = solution_constraints.SolutionConstraints()

  with description('constructor'):
    with it('constructs without error'):
      expect(calling(
          generate_solutions.GenerateSolutions, self.constraints, _source)
      ).not_to(raise_error)

    with it('does not read source until needed'):
      source = mock.Mock(return_value=_source())
      generate_solutions.GenerateSolutions(self.constraints, source)
      expect(source).not_to(have_been_called_once)

  with description('generation') as self:
    with before.each:
      self.source_iter = _source()
      self.source = mock.Mock(return_value=self.source_iter)
      self.ex = generate_solutions.GenerateSolutions(self.constraints, self.source)

    with it('produces solutions'):
      expect(self.ex.solutions()).to(equal(_SOLUTIONS))

    with it('only calls source once'):
      self.ex.solutions()
      self.ex.solutions()
      expect(self.source).to(have_been_called_once)

    with it('constrains solutions'):
      self.constraints.weight_threshold = 1.0
      expect(self.ex.solutions()).to(equal({'early_high': 1.0}))

    with it('only calls source once, even if reconstrained'):
      self.ex.solutions()
      self.constraints.weight_threshold = 0.5
      self.ex.solutions()
      expect(self.source).to(have_been_called_once)

    with it('solutions() returns all results'):
      expect(list(self.ex.solutions().items())).to(equal(
          list(sorted(_SOLUTIONS.items(), key=lambda x: x[1], reverse=True))))

    with it('solutions stream via yield'):
      expect(self.ex.solution).to(equal('early_high'))
      # Prove there are still items left in the iterator:
      expect(calling(next, self.source_iter)).to(equal(
          ('after_early_high', 0.9)))

from puzzle.constraints import solution_constraints
from spec.mamba import *

with description('solution_constraints') as self:
  with before.each:
    self.constraints = solution_constraints.SolutionConstraints()

  with description('has_enumeration'):
    with it('is None initially'):
      expect(self.constraints.solution_enumeration).to(be_none)

    with it('accepts simple enumeration specification'):
      self.constraints.has_enumeration([3])
      expect(self.constraints.is_solution_valid('foo', 1)).to(be_true)

    with it('validates simple enumeration specification'):
      self.constraints.has_enumeration([3])
      expect(self.constraints.is_solution_valid('foobar', 1)).to(be_false)

    with it('accepts complex enumeration specification'):
      self.constraints.has_enumeration([3, 3])
      expect(self.constraints.is_solution_valid('foo bar', 1)).to(be_true)

    with it('validates complex enumeration specification'):
      self.constraints.has_enumeration([3, 3])
      expect(self.constraints.is_solution_valid('foo foobar', 1)).to(be_false)

  with description('length constraints'):
    with it('is None initially'):
      expect(self.constraints.solution_length).to(be_none)
      expect(self.constraints.solution_min_length).to(be_none)

    with it('has_length accepts new value'):
      self.constraints.solution_length = 3
      expect(self.constraints.is_solution_valid('foo', 1)).to(be_true)

    with it('has_length validates new value'):
      self.constraints.solution_length = 3
      expect(self.constraints.is_solution_valid('fo', 1)).to(be_false)
      expect(self.constraints.is_solution_valid('foobar', 1)).to(be_false)

    with it('has_length ignores spaces'):
      self.constraints.solution_length = 3
      expect(self.constraints.is_solution_valid('f o o', 1)).to(be_true)

    with it('is_at_least_length validates new value'):
      self.constraints.solution_min_length = 5
      expect(self.constraints.is_solution_valid('foo', 1)).to(be_false)
      expect(self.constraints.is_solution_valid('foobar', 1)).to(be_true)

    with it('is_at_least_length ignores spaces'):
      self.constraints.solution_min_length = 3
      expect(self.constraints.is_solution_valid('f   o', 1)).to(be_false)
      expect(self.constraints.is_solution_valid('f o o', 1)).to(be_true)

  with description('weight constraints'):
    with it('is not None initially'):
      expect(self.constraints.weight_threshold).not_to(be_none)

    with it('accepts new value'):
      self.constraints.weight_threshold = 0
      expect(self.constraints.is_solution_valid('foobar', 0.1)).to(be_true)

    with it('rejects negative weights'):
      expect(calling(setattr, self.constraints, 'weight_threshold', -1)).to(
          raise_error)

    with it('rejects low weights'):
      self.constraints.weight_threshold = 1
      expect(self.constraints.is_solution_valid('foobar', 0.1)).to(be_false)

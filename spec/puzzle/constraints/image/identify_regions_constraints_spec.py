from puzzle.constraints.image import identify_regions_constraints
from spec.mamba import *


class MethodConstraints(identify_regions_constraints.BaseRegionConstraints):
  _method = identify_regions_constraints.Method.HEXAGONAL_GRID
  key: str = 'sample'

  allow_inactive_modifications = (
      identify_regions_constraints.BaseRegionConstraints.
          _allow_inactive_modifications)


with description('identify_regions_constraints') as self:
  with before.each:
    self.constraints = identify_regions_constraints.IdentifyRegionsConstraints()
    self.method_constraints = MethodConstraints()
    self.pause = self.method_constraints.allow_inactive_modifications

  with it('initially disables method constraints'):
    expect(self.method_constraints.is_modifiable('key')).to(be_false)

  with it('temporarily allows modifications'):
    with self.pause():
      expect(self.method_constraints.is_modifiable('key')).to(be_true)

  with description('register_method_constraint'):
    with it('allows registering methods'):
      expect(calling(
          self.constraints.register_method_constraint,
          self.method_constraints
      )).not_to(raise_error)

    with it('initializes matching constraints (when changed beforehand)'):
      self.constraints.method = (
          identify_regions_constraints.Method.HEXAGONAL_GRID)
      self.constraints.register_method_constraint(self.method_constraints)
      expect(self.method_constraints.is_modifiable('key')).to(be_true)

    with it('notifies and activates matching constraints (when changed later'):
      self.constraints.register_method_constraint(self.method_constraints)
      self.constraints.method = (
          identify_regions_constraints.Method.HEXAGONAL_GRID)
      expect(self.method_constraints.is_modifiable('key')).to(be_true)

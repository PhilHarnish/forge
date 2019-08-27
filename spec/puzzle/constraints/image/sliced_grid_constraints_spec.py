import numpy as np

from data.image import image
from puzzle.constraints.image import identify_regions_constraints, \
  sliced_grid_constraints
from spec.mamba import *

_SOURCE = image.Image(np.zeros((300, 200)))


with description('sliced_grid_constraints.SlicedGridConstraints'):
  with it('constructs without error'):
    expect(
        calling(sliced_grid_constraints.SlicedGridConstraints, _SOURCE)
    ).not_to(raise_error)

with description('sliced_grid_constraints') as self:
  with before.each:
    self.constraints = sliced_grid_constraints.SlicedGridConstraints(
        _SOURCE)
    self.constraints.update_active_for_method(
        identify_regions_constraints.Method.SLICED_GRID)

  with description('is_modifiable'):
    with it('nothing is modifiable when inactive'):
      self.constraints.update_active_for_method(
          identify_regions_constraints.Method.LINES_CLASSIFIER)
      for key in dir(self.constraints):
        expect(calling(self.constraints.is_modifiable, key)).to(equal(False))

    with it('some keys are modifiable when active'):
      self.constraints.update_active_for_method(
          identify_regions_constraints.Method.SLICED_GRID)
      some_modifiable = any(
          self.constraints.is_modifiable(key) for key in dir(self.constraints)
      )
      expect(some_modifiable).to(be_true)

    with it('diminsion divisions cannot be changed when n_divisions is set'):
      self.constraints.n_divisions = 1
      expect(self.constraints.is_modifiable('n_divisions_first')).to(be_false)

    with it('diminsion divisions can be changed when n_divisions is cleared'):
      self.constraints.n_divisions = None
      expect(self.constraints.is_modifiable('n_divisions_first')).to(be_true)

  with description('set_source'):
    with it('changes center if source changes'):
      original = self.constraints.center
      self.constraints.set_source(image.Image(np.zeros((100, 100))))
      expect(original).not_to(equal(self.constraints.center))
      expect(self.constraints.center).to(equal((50, 50)))

    with it('changes dimensions if source changes'):
      original = self.constraints.first
      self.constraints.set_source(image.Image(np.zeros((100, 100))))
      expect(original).not_to(equal(self.constraints.first))
      expect(self.constraints.first).to(equal((-25, 25)))

  with description('dynamic updates'):
    with it('changes dimension ranges if degrees_offset changes'):
      original = self.constraints.first
      self.constraints.degrees_offset = 30
      expect(self.constraints.first).not_to(equal(original))

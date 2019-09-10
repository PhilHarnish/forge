import numpy as np

from data.image import image
from puzzle.constraints.image import identify_regions_constraints, \
  prepare_image_constraints
from puzzle.steps.image import identify_regions, prepare_image
from spec.mamba import *

with description('identify_regions') as self:
  with before.each:
    self.constraints = identify_regions_constraints.IdentifyRegionsConstraints()
    self.data = np.zeros((3, 3))
    self.source = image.Image(self.data)
    self.prepare_image_step = prepare_image.PrepareImage(
        self.source, prepare_image_constraints.PrepareImageConstraints())

  with description('constructor'):
    with it('constructs without error'):
      expect(calling(identify_regions.IdentifyRegions,
          self.prepare_image_step, self.constraints)
      ).not_to(raise_error)

  with description('get_debug_data'):
    with before.each:
      self.step = identify_regions.IdentifyRegions(
          self.prepare_image_step, self.constraints)

    with it('returns ndarray for LINES_CLASSIFIER'):
      self.constraints.method = (
          identify_regions_constraints.Method.LINES_CLASSIFIER)
      expect(self.step.get_debug_data()[0][1]).to(be_a(np.ndarray))

    with it('returns ndarray for SLICED_GRID'):
      self.constraints.method = (
          identify_regions_constraints.Method.SLICED_GRID)
      expect(self.step.get_debug_data()[0][1]).to(be_a(np.ndarray))

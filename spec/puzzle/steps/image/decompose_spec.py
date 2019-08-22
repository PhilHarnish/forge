import numpy as np

from data.image import image
from puzzle.constraints.image import decompose_constraints, \
  prepare_image_constraints
from puzzle.steps.image import decompose, prepare_image
from spec.mamba import *

with description('decompose') as self:
  with before.each:
    self.constraints = decompose_constraints.DecomposeConstraints()
    self.data = np.zeros((3, 3))
    self.source = image.Image(self.data)
    self.prepare = prepare_image.PrepareImage(
        self.source, prepare_image_constraints.PrepareImageConstraints())

  with description('constructor'):
    with it('constructs without error'):
      expect(
          calling(decompose.Decompose, self.prepare, self.constraints)
      ).not_to(raise_error)

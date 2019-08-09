import numpy as np

from data.image import image
from puzzle.constraints.image import prepare_image_constraints
from puzzle.steps.image import prepare_image
from spec.mamba import *

with description('prepare_image') as self:
  with before.each:
    self.constraints = prepare_image_constraints.PrepareImageConstraints()
    self.data = np.zeros((3, 3))
    self.source = image.Image(self.data)

  with description('constructor'):
    with it('constructs without error'):
      expect(
          calling(prepare_image.PrepareImage, self.constraints, self.source)
      ).not_to(raise_error)

  with description('get_result'):
    with before.each:
      self.step = prepare_image.PrepareImage(self.constraints, self.source)

    with it('applies many mutations initially'):
      i = self.step.get_result()
      for mutation in {'normalize', 'invert', 'crop', 'grayscale', 'enhance'}:
        expect(calling(i.has_mutation, mutation)).to(equal(True))

    with it('skips mutations if requested'):
      self.constraints.enhance = False
      self.constraints.grayscale = False
      self.constraints.crop = None
      self.constraints.invert = False
      self.constraints.normalize = False
      i = self.step.get_result()
      for mutation in {'normalize', 'invert', 'crop', 'grayscale', 'enhance'}:
        expect(calling(i.has_mutation, mutation)).to(equal(False))

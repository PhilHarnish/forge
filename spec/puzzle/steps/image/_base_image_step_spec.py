import numpy as np

from data.image import image
from puzzle.constraints import constraints
from puzzle.steps.image import _base_image_step
from spec.mamba import *


class TestConstraints(constraints.Constraints):
  key: str = 'value'


class TestImageStep(_base_image_step.BaseImageStep):
  def _modify_result(self, result: image.Image) -> image.Image:
    return result


with description('_base_image_step') as self:
  with before.each:
    self.data = np.zeros((3, 3))
    self.source = image.Image(self.data)

  with description('constructor'):
    with it('constructs without error'):
      expect(calling(TestImageStep, self.source)).not_to(raise_error)

  with description('get_result'):
    with before.each:
      self.constraints = TestConstraints()
      self.step = TestImageStep(self.source, constraints=[self.constraints])

    with it('returns an image'):
      expect(self.step.get_result()).to(be_a(image.Image))

    with it('returns the image if called repeatedly'):
      first = self.step.get_result()
      expect(self.step.get_result()).to(be(first))

    with it('operates on a fork() of original image'):
      expect(self.step.get_result()).not_to(be(self.source))

    with it('returns a new result if constraints change'):
      first = self.step.get_result()
      self.constraints.key = 'changed'
      expect(self.step.get_result()).not_to(be(first))

  with it('provides debug data'):
    expect(TestImageStep(self.source).get_debug_data().tolist()).to(
        equal(self.data.tolist()))

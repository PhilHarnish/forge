import numpy as np

from data.image import image
from puzzle.constraints.image import prepare_image_constraints
from puzzle.steps.image import _base_image_step

_DEFAULTS = prepare_image_constraints.PrepareImageConstraints()


class PrepareImage(_base_image_step.BaseImageStep):
  _prepare_image_constraints: prepare_image_constraints.PrepareImageConstraints

  def __init__(
      self,
      constraints: prepare_image_constraints.PrepareImageConstraints,
      source: image.Image) -> None:
    super(PrepareImage, self).__init__(source, constraints=(constraints,))
    self._prepare_image_constraints = constraints

  def _modify_result(self, result: image.Image) -> image.Image:
    constraints = self._prepare_image_constraints
    if constraints.normalize:
      result.normalize()
    if constraints.invert:
      result.invert()
    if constraints.crop is not None:
      color = np.array([constraints.crop, constraints.crop, constraints.crop])
      result.crop(color)
    if constraints.grayscale:
      result.grayscale()
    if constraints.enhance:
      result.enhance()
    return result

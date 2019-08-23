import numpy as np

from data.image import image
from puzzle.constraints.image import prepare_image_constraints
from puzzle.steps.image import _base_image_step


class PrepareImage(_base_image_step.BaseImageStep):
  _prepare_image_constraints: prepare_image_constraints.PrepareImageConstraints

  def __init__(
      self,
      source: image.Image,
      constraints: prepare_image_constraints.PrepareImageConstraints) -> None:
    super(PrepareImage, self).__init__(source, constraints=(constraints,))
    self._prepare_image_constraints = constraints

  def _modify_result(self, result: image.Image) -> image.Image:
    constraints = self._prepare_image_constraints
    if constraints.normalize:
      result.normalize()
    if constraints.invert:
      result.invert()
    if constraints.crop is not None:
      color = np.array(constraints.crop)
      result.crop(color)
    if constraints.grayscale:
      result.grayscale()
    if constraints.enhance:
      result.enhance()
    return result

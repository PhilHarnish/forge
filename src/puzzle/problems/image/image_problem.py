"""
Steps:
2. For each color band
  1. Compute components
  2. Identify components
  3. Erase identified components from parent
"""

import numpy as np

from data.image import image
from puzzle.constraints.image import decompose_constraints, \
  prepare_image_constraints
from puzzle.problems import problem
from puzzle.steps.image import decompose, prepare_image


class ImageProblem(problem.Problem):
  _source_image: image.Image
  _prepare_image: prepare_image.PrepareImage

  def __init__(self, name: str, data: np.ndarray, *args, **kwargs) -> None:
    super(ImageProblem, self).__init__(name, data, *args, **kwargs)
    self._source_image = image.Image(data)
    self._prepare_image = prepare_image.PrepareImage(
        self._source_image,
        prepare_image_constraints.PrepareImageConstraints())
    self._decompose = decompose.Decompose(
        self._prepare_image,
        decompose_constraints.DecomposeConstraints())
    self._solutions_generator.depends_on(self._decompose)

  @staticmethod
  def score(data: problem.ProblemData) -> float:
    if not isinstance(data, np.ndarray):
      return 0
    if data.dtype == np.uint8:
      return 1
    return .5

  def __str__(self) -> str:
    return '<image data>'

  def _solve(self) -> dict:
    return {}

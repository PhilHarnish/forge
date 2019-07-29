import numpy as np

from puzzle.problems import problem


class ImageProblem(problem.Problem):
  def __init__(self, name: str, data: np.ndarray, *args, **kwargs) -> None:
    super(ImageProblem, self).__init__(name, data, *args, **kwargs)

  @staticmethod
  def score(data: problem.ProblemData) -> float:
    if not isinstance(data, np.ndarray):
      return 0
    if data.dtype == np.uint8:
      return 1
    return .5

  def __str__(self) -> str:
    return '<image data>'

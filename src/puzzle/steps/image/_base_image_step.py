from typing import Any, List, NamedTuple, Optional, Tuple

import numpy as np

from data.image import image
from puzzle.steps import step


class ImageChangeEvent(NamedTuple):
  pass


class BaseImageStep(step.Step):
  _source: image.Image
  _result: Optional[image.Image]

  def __init__(self,
      source: image.Image,
      dependencies: Optional[step.Dependencies] = None,
      constraints: Optional[step.Constraints] = None) -> None:
    super(BaseImageStep, self).__init__(
        dependencies=dependencies,
        constraints=constraints)
    if constraints:
      for constraint in constraints:
        constraint.subscribe(self._on_constraints_changed)
    self._source = source
    self._result = None

  def get_result(self) -> image.Image:
    if self._result is None:
      self._result = self._modify_result(self._get_new_source())
    return self._result

  def get_debug_data(self) -> List[Tuple[str, np.ndarray]]:
    return self.get_result().get_debug_data(replay_mutations=True)

  def _get_new_source(self) -> image.Image:
    return self._source.fork()

  def _modify_result(self, result: image.Image) -> image.Image:
    raise NotImplementedError()

  def _on_constraints_changed(self, change: Any) -> None:
    del change
    self._result = None
    self._subject.on_next(ImageChangeEvent())

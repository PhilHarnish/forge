import itertools

import numpy as np


class Component(object):
  _image: np.ndarray

  def __init__(self, image: np.ndarray) -> None:
    self._image = image.copy()

  def __hash__(self) -> int:
    return hash(tuple(itertools.chain(
      self._image.shape,
      self._image.flat,
    )))

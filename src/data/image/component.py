import itertools

import numpy as np


class Component(object):
  image: np.ndarray

  def __init__(self, image: np.ndarray) -> None:
    self.image = image.copy()
    self.image.setflags(write=False)

  def __hash__(self) -> int:
    return hash(tuple(itertools.chain(
      self.image.shape,
      self.image.flat,
    )))

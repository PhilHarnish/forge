import itertools
from typing import Dict

import numpy as np

Labels = Dict[str, str]


class Component(object):
  image: np.ndarray
  labels: Labels

  def __init__(self, image: np.ndarray, labels: Labels = None) -> None:
    self.image = image.copy()
    self.image.setflags(write=False)
    self.labels = {}
    if labels:
      self.labels.update(labels)

  def __hash__(self) -> int:
    return hash(tuple(itertools.chain(
      self.image.shape,
      self.image.flat,
    )))

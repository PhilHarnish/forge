import itertools
from typing import Dict, NamedTuple, Optional

import numpy as np

Labels = Dict[str, str]
class Offset(NamedTuple):
  top: int
  left: int


class Component(object):
  image: np.ndarray
  labels: Labels

  def __init__(
      self,
      image: np.ndarray,
      labels: Optional[Labels] = None) -> None:
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

  def __repr__(self) -> str:
    if self.labels:
      labels = ', labels=%r' % self.labels
    else:
      labels = ''
    return '%s(<image>%s)' % (self.__class__.__name__, labels)

  def __str__(self) -> str:
    return str(self.labels)


class PositionedComponent(Component):
  offset: Offset

  def __init__(
      self,
      image: np.ndarray,
      offset: Offset,
      labels: Optional[Labels] = None) -> None:
    super().__init__(image, labels=labels)
    self.offset = offset

  def __hash__(self) -> int:
    return hash((*self.offset, super().__hash__()))

  def __repr__(self) -> str:
    offset_replacement = '<image>, offset=%r' % (self.offset,)
    return super().__repr__().replace('<image>', offset_replacement)

  def __str__(self) -> str:
    return '%s @ %s' % (super().__str__(), tuple(self.offset))

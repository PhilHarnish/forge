import itertools
from typing import Dict, NamedTuple, Optional

import numpy as np

Labels = Dict[str, str]
class Offset(NamedTuple):
  top: int
  left: int


_ORIGIN = Offset(0, 0)


class Component(object):
  image: np.ndarray
  offset: Offset
  labels: Labels

  def __init__(
      self,
      image: np.ndarray,
      offset: Optional[Offset] = None,
      labels: Optional[Labels] = None) -> None:
    self.image = image.copy()
    self.image.setflags(write=False)
    if offset is None:
      offset = _ORIGIN
    self.offset = offset
    self.labels = {}
    if labels:
      self.labels.update(labels)

  def __hash__(self) -> int:
    return hash(tuple(itertools.chain(
      self.image.shape,
      self.image.flat,
    )))

  def __repr__(self) -> str:
    if self.offset is _ORIGIN:
      offset = ''
    else:
      offset = ', offset=%r' % (self.offset,)
    if self.labels:
      labels = ', labels=%r' % self.labels
    else:
      labels = ''
    return 'Component(<image>%s%s)' % (offset, labels)

  def __str__(self) -> str:
    if self.offset is _ORIGIN:
      return str(self.labels)
    return '%s @ %s' % (self.labels, tuple(self.offset))

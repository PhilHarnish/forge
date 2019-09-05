from typing import Iterable, Tuple

from util.geometry.np2d import Point

Divisions = Iterable[Tuple[float, Point, Point, float]]


class LineSpecification(object):
  def __iter__(self) -> Iterable[Divisions]:
    raise NotImplementedError()

  def __len__(self) -> int:
    raise NotImplementedError()

import itertools
from typing import Iterable, Tuple

import numpy as np

Point = np.ndarray
Segment = Tuple[Point, Point]
Contour = np.ndarray


def iter_segments(points: np.ndarray) -> Iterable[Segment]:
  """Given points A, B, ...N returns (A, B), (B, ...), (..., N), (N, A)."""
  # "contour" frequently has shape (N, 1, 2); remove "1" middle layer.
  if len(points.shape) > 2:
    size = points.size
    points = points.view()
    points.shape = (size // 2, 2)
  return zip(
      points,
      itertools.chain(points[1:], points[:1]))


def orientation(a: Point, b: Point, c: Point) -> int:
  """Returns 0 for colinear, and -1/1 for CW and CCW points."""
  return int(np.sign(np.cross(b-a, c-b)))


def point_to_point_distance(point1: Point, point2: Point) -> float:
  return np.hypot(*(point1 - point2))


def point_to_segment_distance(point: Point, segment: Segment) -> float:
  s1, s2 = segment
  dx_dy = s2 - s1
  # Find a multiple of dx/dy (relative to s1) which is closest to point.
  t = np.dot(point - s1, dx_dy) / np.dot(dx_dy, dx_dy)
  if t < 0:  # Near 1st segment endpoint.
    dx_dy = point - s1
  elif t > 1:  # Near 2nd segment endpoint.
    dx_dy = point - s2
  else:  # `t * dx/dy` distance from s1.
    dx_dy = point - (s1 + t * dx_dy)
  return np.hypot(*dx_dy)


def segments_intersect(s1: Segment, s2: Segment) -> bool:
  """Returns True if two line segments intersect. Endpoints ignored."""
  s1p1, s1p2 = s1
  s2p1, s2p2 = s2
  return (
    orientation(s1p1, s1p2, s2p1) != orientation(s1p1, s1p2, s2p2) and
    orientation(s2p1, s2p2, s1p1) != orientation(s2p1, s2p2, s1p2)
  )

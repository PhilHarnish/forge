"""Library for performing 2D geometric operations on numpy arrays.

May also make use of cv2 where faster.

The following performance notes are on implementations made obsolete by faster
or more accurate options.

Converting two segments into a quadrilateral:
```
def segments_to_contour(s1, s2, may_intersect=False):
  s1p1, s1p2 = s1
  s2p1, s2p2 = s2
  with segment_to_hull.benchmark('cv2'):
    # This is 4-5x faster than 'np' below but produces different results.
    # Consider two segments forming a T: the hull has 3 points, not 4.
    hull = cv2.convexHull(np.array([s1p1, s1p2, s2p1, s2p2]), False)
  with segment_to_hull.benchmark('np'):
    if may_intersect and np2d.segments_intersect(s1, s2):
      # Swap endpoints to break intersection.
      s1p1, s2p1 = s2p1, s1p1
    orientation_to_s2p1 = np2d.orientation(s1p1, s1p2, s2p1)
    orientation_to_s2p2 = np2d.orientation(s1p2, s2p1, s2p2)
    if orientation_to_s2p1 != orientation_to_s2p2:
      s2p1, s2p2 = s2p2, s2p1
  return np.array((s1p1, s1p2, s2p1, s2p2))
```

Calculating area of a quadrilateral:
```
def segment_area(s1, s2):
  contour = segments_to_contour(s1, s2)
  with perf_segment_area.benchmark('np'):
    if len(contour.shape) > 2:
      size = contour.size
      contour = contour.view()
      contour.shape = (size // 2, 2)
    x = contour[:, 0]
    y = contour[:, 1]
    n = len(x)
    shift_up = np.arange(-n + 1, 1)
    shift_down = np.arange(-1, n - 1)
    area1 = np.abs((x * (y.take(shift_up) - y.take(shift_down))).sum() / 2)
  with perf_segment_area.benchmark('cv2'):
    # This is 7-8x faster.
    area2 = cv2.contourArea(contour)
  if not np.isclose(area1, area2):
    # Observed area values are identical for both methods.
    print('not close:', area1, area2)
    print('segments:', s1, s2)
  return area2
```

Rotating s1 with y=0; verifying x overlap between s1 and s2:
```
def slope(s):
  a, b = s
  dx, dy = b - a
  if dx == 0:
    return np.pi / 2
  return np.arctan(dy / dx)

_SIMILAR_ANGLES = math.pi / 10
def segments_overlap(s1, s2):
  slope1 = slope(s1)
  slope2 = slope(s2)
  if abs(slope1 - slope2) >= _SIMILAR_ANGLES:
    return False
  # Undo slope1's rotation on s1 and s2.
  c, s = np.cos(slope1), np.sin(slope1)
  rotational_transformation = np.array(((c, s), (-s, c)))
  s1 = np.array([
      np.dot(rotational_transformation, s1[0]),
      np.dot(rotational_transformation, s1[1]),
  ], dtype=np.int32)
  s2 = np.array([
      np.dot(rotational_transformation, s2[0]),
      np.dot(rotational_transformation, s2[1]),
  ], dtype=np.int32)
  left1 = s1[0][0]
  right1 = s1[1][0]
  if left1 > right1:
    left1, right1 = right1, left1
  left2 = s2[0][0]
  right2 = s2[1][0]
  if left2 > right2:
    left2, right2 = right2, left2
  # Throw out segments which don't overlap in x.
  if left1 > left2:
    left1, left2 = left2, left1
    right1, right2 = right2, right1
  return not (right1 < left2)
```
"""

import itertools
from typing import Iterable, Tuple

import numpy as np

Point = np.ndarray
Segment = Tuple[Point, Point]
Contour = np.ndarray


def iter_segments(points: Contour) -> Iterable[Segment]:
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

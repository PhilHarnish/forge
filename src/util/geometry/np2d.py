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
"""

import itertools
import math
from typing import Iterable, Optional, Tuple, Union

import numpy as np

Point = Union[np.ndarray, Tuple[float, float]]
PolarLine = Tuple[float, float]
Segment = Tuple[Point, Point]
Contour = np.ndarray


def distance_to_bounding_box(
    width: int, height: int, x: int, y: int, theta: float) -> float:
  """Returns distance from (x, y) to width x height box with angle theta."""
  cos_theta = math.cos(theta)
  if cos_theta > 0:  # Pointing right.
    dx = width - x
  else:  # Pointing left.
    dx = -x
  sin_theta = math.sin(theta)
  if sin_theta > 0:  # Pointing up (down in an image).
    dy = height - y
  else:
    dy = -y
  if cos_theta:
    hypotenuse_to_x = dx / cos_theta
  else:
    hypotenuse_to_x = float('inf')
  if sin_theta:
    hypotenuse_to_y = dy / sin_theta
  else:
    hypotenuse_to_y = float('inf')
  return min(hypotenuse_to_x, hypotenuse_to_y)  # First intercept.


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


_SIMILAR_ANGLES = math.pi / 7
def overlap(
    s1: Segment, s2: Segment, slope_threshold: float = _SIMILAR_ANGLES,
    gap_threshold: Optional[float] = None) -> float:
  """Rotate s1, s2 such that y=0 for s1; measure x overlap between s1 and s2."""
  slope1, slope2, slope_delta = slopes(s1, s2)
  if slope_delta >= slope_threshold:
    return 0
  # Undo slope1's rotation on s1 and s2.
  c = np.cos(slope1)
  s = np.sin(slope1)
  rotational_transformation = np.array(((c, s), (-s, c)))
  s1p1 = np.dot(rotational_transformation, s1[0])
  s1p2 = np.dot(rotational_transformation, s1[1])
  s2p1 = np.dot(rotational_transformation, s2[0])
  s2p2 = np.dot(rotational_transformation, s2[1])
  left1 = s1p1[0]
  right1 = s1p2[0]
  if left1 > right1:
    left1, right1 = right1, left1
  left2 = s2p1[0]
  right2 = s2p2[0]
  if left2 > right2:
    left2, right2 = right2, left2
  if left1 > left2:
    left1, left2 = left2, left1
    right1, right2 = right2, right1
  avg_width = ((right1 - left1) + (right2 - left2)) / 2
  if gap_threshold is None:
    # Use average line width if no threshold was specified.
    gap_threshold = avg_width
  max_delta = max(
      abs(s2p1[1] - s1p1[1]),
      abs(s2p2[1] - s1p1[1]),
  )
  if max_delta > gap_threshold:
    # s2 is too far away from s1.
    return 0
  # Return overlap as % of average.
  return (right1 - left2) / avg_width


def point_intersect_box(point, theta: float, width: int, height: int) -> bool:
  """Returns line extending from `point` with angle theta intersects box."""
  pt_x, pt_y = point
  if (0 < pt_x < width) and (0 < pt_y < height):
    return True
  x_edges = 0
  x_distance = 0
  y_edges = 0
  y_distance = 0
  tan_theta = math.tan(theta)
  for x in (0, width):
    # Solve for y.
    dx = pt_x - x
    # If tan_theta is bonkers big (straight up/down) then this fails.
    dy = tan_theta * dx
    y_distance += abs(dy)
    if 0 <= pt_y - dy <= height:
      y_edges += 1
  for y in (0, height):
    # Solve for x.
    dy = pt_y - y
    if tan_theta:
      dx = dy / tan_theta
    else:
      dx = float('inf')
    x_distance += abs(dx)
    if 0 <= pt_x - dx <= width:
      x_edges += 1
  vertical = y_distance > 1 and x_edges == 2
  horizontal = x_distance > 1 and y_edges == 2
  diagonal = x_edges >= 1 and y_edges >= 1
  return vertical or horizontal or diagonal


def point_to_point_distance(point1: Point, point2: Point) -> float:
  # NB: This is faster than using np.hypot.
  x1, y1 = point1
  x2, y2 = point2
  return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


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


def polar_line_intersect(line1: PolarLine, line2: PolarLine) -> Point:
  rho1, theta1 = line1
  rho2, theta2 = line2
  a = np.array([
    [math.cos(theta1), math.sin(theta1)],
    [math.cos(theta2), math.sin(theta2)],
  ])
  b = np.array([[rho1], [rho2]])
  x, y = np.linalg.solve(a, b)
  return float(x), float(y)


def slope(s: Segment) -> float:
  """Returns the slope, in radians, for a given segment."""
  a, b = s
  dx, dy = b - a
  if dx == 0:
    return np.pi / 2
  return np.arctan(dy / dx)


def slopes(s1: Segment, s2: Segment) -> Tuple[float, float, float]:
  slope1 = slope(s1)
  slope2 = slope(s2)
  delta = (slope1 - slope2) % math.pi
  delta = min(delta, math.pi - delta)
  return slope1, slope2, delta


def segments_intersect(s1: Segment, s2: Segment) -> bool:
  """Returns True if two line segments intersect. Endpoints ignored."""
  s1p1, s1p2 = s1
  s2p1, s2p2 = s2
  return (
    orientation(s1p1, s1p2, s2p1) != orientation(s1p1, s1p2, s2p2) and
    orientation(s2p1, s2p2, s1p1) != orientation(s2p1, s2p2, s1p2)
  )

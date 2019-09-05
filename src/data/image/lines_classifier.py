import math
from typing import Any, Iterable, List, Optional, Tuple

import cv2
import numpy as np

from data import max_heap
from data.image import coloring, divide_distances_evenly, image, model
from puzzle.constraints.image import lines_classifier_constraints
from util.geometry import np2d

Point = Tuple[float, float]
Group = List[image.PolarLine]


_SLICES = (2, 3, 4, 6)
_THETA_TARGETS = [(n, math.pi / n) for n in _SLICES]


# When True, a considerable amount of debug output is produced.
DEBUG = False


class _LineGroup(object):
  _group: Group
  _constraints: lines_classifier_constraints.LinesClassifierConstraints
  _center: Point
  _theta: float
  _intersections: List[Point]
  _start: Optional[Point]
  _end: Optional[Point]
  _shift: Optional[Point]
  _line_width: Optional[int]
  _n_divisions: Optional[int]

  def __init__(
      self,
      group: Group,
      constraints: lines_classifier_constraints.LinesClassifierConstraints,
      center: Point) -> None:
    self._group = group
    self._constraints = constraints
    self._center = center
    # Clamping improves results for arrow.png and rowsgarden.png.
    self._theta = _clamp_theta(
        group[len(group) // 2][1],
        math.radians(self._constraints.angle_resolution_degrees))
    self._intersections = []
    self._start = None
    self._end = None
    self._shift = None
    self._line_width = None
    self._n_divisions = None

  @property
  def start(self) -> Point:
    self._calculate()
    return self._start

  @property
  def end(self) -> Point:
    self._calculate()
    return self._end

  @property
  def line_width(self) -> int:
    self._calculate()
    return self._line_width

  def points(self) -> Iterable[Point]:
    for _, point in self._enumerate_points():
      yield point

  def get_slope_divisions(self) -> model.Divisions:
    max_distance = sum(self._center) * 2
    right_angle = self._theta + math.pi / 2
    dx = round(math.cos(right_angle) * max_distance)
    dy = round(math.sin(right_angle) * max_distance)
    for i, (x, y) in self._enumerate_points():
      yield (
        self._theta,
        (round(x - dx), round(y - dy)), (round(x + dx), round(y + dy)),
        i / self._n_divisions)

  def draw_debug_data(self, out: np.ndarray, color: coloring.Color) -> None:
    self._calculate()
    dim = max(self._center) * 3  # Large enough to exceed image diagonally.
    for line in self._group:
      _draw_hough_line(out, line, color, dim)
    for x, y in self._intersections:
      cv2.circle(out, (int(x), int(y)), 2, color, thickness=1)
    for x, y in self.points():
      cv2.circle(out, (int(x), int(y)), 2, color, thickness=3)
    if self._start:
      x, y = self._start
      shift_x, shift_y = self._shift
      cv2.line(out, self._start, (x - shift_x, y - shift_y), (255, 255, 255))
      for x, y in (self._start, self._end):
        cv2.circle(out, (int(x), int(y)), 3, (255, 255, 255), thickness=4)
        cv2.circle(out, (int(x), int(y)), 1, color, thickness=2)

  def separation(self, other: '_LineGroup') -> float:
    return abs(self._theta - other._theta)

  def __len__(self) -> int:
    return len(self._group)

  def __iter__(self) -> Iterable[image.PolarLine]:
    return iter(self._group)

  def _calculate(self) -> None:
    if self._start is not None:
      return  # Calculation already complete.
    center = self._center
    center_x, center_y = center
    center_theta = math.atan2(center_x, -center_y)
    center_length = math.sqrt(center_x**2 + center_y**2)
    # Find line perpendicular to median_theta which passes through center.
    intersection_theta = self._theta - math.pi / 2
    inside_angle = center_theta - intersection_theta
    adjusted_length = math.sin(inside_angle) * center_length
    center_line = (adjusted_length, intersection_theta)
    self._intersections = [
      np2d.polar_line_intersect(center_line, line) for line in self._group
    ]
    # Find the point farthest from the center.
    intersections = sorted(
        self._intersections,
        key=lambda x: np2d.point_to_point_distance(center, x))
    pt_start = intersections[-1]
    distances = [
      np2d.point_to_point_distance(pt_start, pt) for pt in intersections
    ]

    combined = sorted(zip(intersections, distances), key=lambda x: x[1])
    intersections, distances = [list(t) for t in zip(*combined)]
    if DEBUG:
      print('_' * 80)
      print('ANGLE: %f' % math.degrees(self._theta))
      print(', '.join('(%d, %d)' % pt for pt in intersections))
    first, last, n_divisions, shift = (
      divide_distances_evenly.divide_distances_evenly(
          distances,
          required_divisions_ratio=self._constraints.required_divisions_ratio,
          max_consecutive_missing=self._constraints.max_consecutive_missing,
          anchor_resolution_px=self._constraints.anchor_resolution_px,
          division_distance_resolution_px=(
              self._constraints.division_distance_resolution_px),
    ))
    x1, y1 = intersections[first]
    x2, y2 = intersections[last]
    full_distance = distances[last] - distances[first]
    slope = math.atan2(y2 - y1, x2 - x1)
    shift_x = math.cos(slope) * full_distance * shift
    shift_y = math.sin(slope) * full_distance * shift
    self._shift = (round(shift_x), round(shift_y))
    self._start = (round(x1 + shift_x), round(y1 + shift_y))
    self._end = (round(x2 + shift_x), round(y2 + shift_y))
    self._line_width = round(max(abs(shift_x), abs(shift_y)))
    self._n_divisions = n_divisions

  def _enumerate_points(self) -> Iterable[Tuple[int, Point]]:
    if self.start is None:
      return
    center_x, center_y = self._center
    width, height = round(center_x * 2), round(center_y * 2)
    x1, y1 = self.start
    x2, y2 = self.end
    dx = x2 - x1
    dy = y2 - y1
    n_divisions = self._n_divisions
    # NOTE: angle increases by 90 degrees because Hough lines assume 0 degrees
    # is North (and then progresses clockwise).
    theta = math.atan2(dy, dx) + math.pi / 2
    # Find first point (in negative direction) which still intersects box.
    scan_pos = 0
    scan_pt = self.start
    while np2d.point_intersect_box(scan_pt, theta, width, height):
      scan_pos -= 1
      scan_x = x1 + (dx * scan_pos) / n_divisions
      scan_y = y1 + (dy * scan_pos) / n_divisions
      scan_pt = (scan_x, scan_y)
    while scan_pos < n_divisions or np2d.point_intersect_box(
        scan_pt, theta, width, height):
      scan_pos += 1
      scan_x = x1 + (dx * scan_pos) / n_divisions
      scan_y = y1 + (dy * scan_pos) / n_divisions
      scan_pt = (scan_x, scan_y)
      yield scan_pos, scan_pt


class _GridLineSpecification(model.LineSpecification):
  _groups: List[_LineGroup]
  _constraints: lines_classifier_constraints.LinesClassifierConstraints
  _grid: Optional[np.ndarray]
  _score: Optional[float]

  def __init__(
      self,
      groups: List[_LineGroup],
      constraints: lines_classifier_constraints.LinesClassifierConstraints,
  ) -> None:
    self._groups = groups
    self._constraints = constraints
    self._grid = None
    self._score = None

  def score(self, source: image.Image) -> float:
    if any(group.start is None for group in self._groups):
      self._score = 0
    if self._score is not None:
      return self._score
    height, width = source.shape[:2]
    max_dim = max(width, height)
    grid = np.zeros(source.shape)
    for line_group in self._groups:
      x1, y1 = line_group.start
      x2, y2 = line_group.end
      dx = x2 - x1
      dy = y2 - y1
      # NOTE: angle increases by 90 degrees because Hough lines assume 0 degrees
      # is North (and then progresses clockwise).
      group_theta = math.atan2(dy, dx) + math.pi / 2
      line_dx = math.cos(group_theta) * max_dim
      line_dy = math.sin(group_theta) * max_dim
      for pt_x, pt_y in line_group.points():
        # NOTE: line_width increases as confidence in line_group decreases.
        cv2.line(
            grid, (round(pt_x - line_dx), round(pt_y - line_dy)),
            (round(pt_x + line_dx), round(pt_y + line_dy)), 255,
            thickness=self._constraints.image_dilate_px + line_group.line_width)
    self._grid = grid
    self._score = source.mask_nonzero(grid) / np.count_nonzero(grid)
    return self._score

  def get_debug_data(self) -> np.ndarray:
    return self._grid

  def __iter__(self) -> Iterable[model.Divisions]:
    for group in self._groups:
      yield group.get_slope_divisions()

  def __len__(self) -> int:
    return len(self._groups)


class LinesClassifier(object):
  _source: image.Image
  _constraints: lines_classifier_constraints.LinesClassifierConstraints
  _line_groups: Optional[List[_LineGroup]]

  def __init__(
      self,
      source: image.Image,
      constraints: lines_classifier_constraints.LinesClassifierConstraints
  ) -> None:
    # TODO: Allow caller to specify n divisions, division width,
    #  start/end points.
    self._source = source
    self._constraints = constraints
    self._line_groups = None

  def line_specs(self) -> Iterable[_GridLineSpecification]:
    if len(self._processed_line_groups()) < 2:
      return
    results = max_heap.MaxHeap()

    # Analyze lines.
    # Deduce the interesting angles for source image.
    for groups in self._match_groups():
      score = groups.score(self._source)
      if score:
        results.push(score, groups)

    while results:
      yield results.pop()

  def get_debug_data(self) -> np.ndarray:
    data = cv2.cvtColor(self._source.get_debug_data(), cv2.COLOR_GRAY2RGB)
    n_groups = len(self._processed_line_groups())
    for group, color in zip(
        self._processed_line_groups(), coloring.colors(n_groups)):
      group.draw_debug_data(data, color)
    return data

  def _processed_line_groups(self) -> List[_LineGroup]:
    if self._line_groups is not None:
      return self._line_groups
    kernel = np.ones(
        (self._constraints.image_dilate_px, self._constraints.image_dilate_px))
    canny = self._source.fork().canny(
        self._constraints.canny_aperture_px).dilate(kernel)
    height, width = self._source.shape[:2]
    for i in self._constraints.hough_lines_threshold_fractions:
      threshold = int(min(width, height) * i)
      # NOTE: "1" is the resolution for rho.
      # NOTE: "0, 0" enables "classic" Hough lines.
      hough_lines = canny.hough_lines(
          math.radians(self._constraints.angle_resolution_degrees), threshold)
      if (hough_lines is not None and
          len(hough_lines) > self._constraints.hough_lines_minimum_lines):
        hough_lines = sorted(hough_lines, key=lambda x: x[0][1])
        groups = _group_lines_by_theta(
            hough_lines, math.radians(self._constraints.angle_cluster_degrees))
        height, width = self._source.shape[:2]
        center = (int(width / 2), int(height / 2))
        self._line_groups = [
          _LineGroup(group, self._constraints, center) for group in groups
          if len(group) >= 2
        ]
        break
    else:
      self._line_groups = []
    return self._line_groups

  def _match_groups(self) -> Iterable[_GridLineSpecification]:
    """Attempt to match up groups of lines based on the periodicity of theta."""
    line_groups = self._processed_line_groups()
    n_groups = len(line_groups)
    threshold = math.radians(self._constraints.angle_cluster_degrees)
    for n_slices, pi_slice in _THETA_TARGETS:
      for i, group in enumerate(line_groups):
        matched_group = [group]
        for j in range(i + 1, n_groups):
          next_group = self._line_groups[j]
          deviation = _angle_slice_remainder(
              group.separation(next_group), pi_slice)
          if deviation < threshold:
            matched_group.append(next_group)
        if len(matched_group) < n_slices:
          continue
        yield _GridLineSpecification(matched_group, self._constraints)


def _group_lines_by_theta(
    lines: List[image.HoughLine], threshold: float) -> List[Group]:
  last = lines[0][0][1]
  group = [tuple(lines[0][0])]
  groups = [group]
  for line in lines[1:]:
    theta = line[0][1]
    if theta - last > threshold:
      group = []
      groups.append(group)
    group.append(tuple(line[0]))
    last = theta
  # See if the highest angles are similar to starting angles.
  if (groups[0][0][1] + math.pi - last) < threshold:
    last_group = groups.pop()
    last_group.extend(groups[0])
    groups[0] = last_group
  return groups


def _clamp_theta(theta: float, angle_resolution: float) -> float:
  for n in _SLICES:
    pi_slice = math.pi / n
    epsilon = _angle_slice_remainder(theta, pi_slice)
    if epsilon < angle_resolution:
      multiple = round(theta / pi_slice)
      return pi_slice * multiple
  return theta


def _angle_slice_remainder(angle: float, pi_slice: float) -> float:
  delta_remainder = angle % pi_slice
  return min(delta_remainder, pi_slice - delta_remainder)


def _draw_hough_line(
    dst: np.ndarray, line: image.PolarLine, color: Any, dim: float) -> None:
  # NOTE: For Hough lines, theta starts North, proceeds clockwise such that
  # 90deg is East. Rho increases from 0 at top-left to +inf going South.
  rho, theta = line
  a = math.cos(theta)
  b = -math.sin(theta)
  x = a * rho
  y = -b * rho
  cv2.line(
      dst,
      (int(x + dim * b), int(y + dim * a)),
      (int(x - dim * b), int(y - dim * a)),
      color, 1)

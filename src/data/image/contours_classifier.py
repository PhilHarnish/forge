import math
from typing import Dict, Tuple, List

import cv2
from sklearn import neighbors
import numpy as np

from data.image import coloring, image, cell, model, edge, component
from util.geometry import np2d

show = lambda *args: None  # DO NOT SUBMIT.
FOCUS = []  # DO NOT SUBMIT.


class ContoursClassifier(object):
  def classify(self, source: image.Image) -> None:
    height, width = source.shape
    area_threshold = (width * height) / 4  # Maximum allowed empty space.
    #show('working on (%dx%d)' % (width, height), source.get_debug_data())
    # DO NOT SUBMIT: Remove "get_debug_data".
    im2, contours, hierarchy = cv2.findContours(
        source.get_debug_data(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # hierarchy initially has shape (1, LEN, 4); reshape to (LEN, 4).
    hierarchy = hierarchy.reshape(hierarchy.shape[-2:])

    filtered = process_contours(contours, hierarchy, 0, [], area_threshold)

    n_neighbors = 9  # Assumes 3x3 grid of 2d squares.
    nearest_neighbors = neighbors.NearestNeighbors(n_neighbors)
    nearest_neighbors.fit([(c.cX, c.cY) for c in filtered])

    focus_points = FOCUS

    cells = {}

    # 840 / 701.71u -> 479 / 388.37u.
    visited = set()
    # DO NOT SUBMIT: Debugging only.
    image = np.zeros((height, width, 3), np.uint8)
    for target in filtered:
      focused = not focus_points or int(target.name) in focus_points
      d, n = nearest_neighbors.kneighbors([(target.cX, target.cY)], n_neighbors=n_neighbors)
      colors = coloring.colors(n_neighbors)
      target.draw_on(image, color=(128, 128, 128), bold=focused)
      for dist, pos, color in zip(*d, *n, colors):
        c = filtered[pos]
        if focus_points and int(c.name) not in focus_points:
          continue
        if c.name < target.name:
          key = '%s:%s' % (c.name, target.name)
        else:
          key = '%s:%s' % (target.name, c.name)
        dupe = key in visited
        if dupe:
          continue
        visited.add(key)
        if dist:
          segments = wall_segments(target, c)
          if segments:
            segment = _best_average_segment(segments)
            _link_cells(source, cells, target, c, segment)
            cv2.line(image, (target.cX, target.cY), (c.cX, c.cY), (128, 0, 0), 2)
            cv2.line(image, tuple(segment[0]), tuple(segment[1]), coloring.WHITE, 2)
    show('completed', image)


class Contour(object):
  def __init__(self, name, original):
    self.name = name
    self.original = original
    self.moments = cv2.moments(original)
    self.area = self.moments['m00']
    if self.area:
      self.cX = int((self.moments["m10"] / self.moments["m00"]))
      self.cY = int((self.moments["m01"] / self.moments["m00"]))
    else:
      self.cX = 0
      self.cY = 0
    self.center = np.array((self.cX, self.cY))
    self.perimeter = cv2.arcLength(original, True)
    if self.area > 5000:
      perimeter_scale = .005
    else:
      perimeter_scale = .05
    self.approx = cv2.approxPolyDP(original, perimeter_scale * self.perimeter, True)
    self.convex = cv2.isContourConvex(self.approx)

  def draw_on(self, image, color=(0, 255, 0), bold=False):
    cv2.drawContours(image, [self.approx], -1, color, 1)
    if bold:
      font_weight = 2
    else:
      font_weight = 1
    cv2.putText(
      image, self.name, (self.cX - 9, self.cY + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), font_weight)


def _link_cells(
    source: image.Image,
    cells: Dict[Contour, cell.Cell],
    a: Contour, b: Contour,
    segment: np2d.Segment) -> None:
  if a in cells:
    cell_a = cells[a]
  else:
    cell_a = cells.setdefault(a, _make_cell(source, a.approx))
  if b in cells:
    cell_b = cells[b]
  else:
    cell_b = cells.setdefault(b, _make_cell(source, b.approx))
  cell_a.neighbors(edge.Edge(segment), cell_b)


def _make_cell(source: image.Image, perimeter_points: np.ndarray) -> cell.Cell:
  x, y, width, height = cv2.boundingRect(perimeter_points)
  return cell.Cell(
      source.extract_rect(x, y, width, height), component.Offset(x, y),
      perimeter_points)


def create_contour_instances(contours, hierarchy, pos, acc):
  total_area = 0
  result = []
  while pos != -1:
    contour_instance = Contour(str(pos), contours[pos])
    if contour_instance.area:
      total_area += contour_instance.area
      result.append(contour_instance)
    pos, _, _, _ = hierarchy[pos]
  return result, total_area


def process_contours(contours, hierarchy, pos, acc, area_threshold):
  #if n_siblings(hierarchy, pos) > 5:
  siblings, area = create_contour_instances(contours, hierarchy, pos, acc)
  acc.extend(siblings)
  # if area > area_threshold:
  #   sibling_area_threshold = area / 1000
  #   filtered = [sibling for sibling in siblings if sibling.area > sibling_area_threshold]
  #   if len(filtered) > 5:
  #     acc.extend(filtered)
  while pos != -1:
    pos, _, child, _ = hierarchy[pos]
    if child:
      process_contours(contours, hierarchy, child, acc, area_threshold)
  return acc



def wall_segments(
    c1: Contour, c2: Contour) -> List[Tuple[np2d.Segment, np2d.Segment, float]]:
  result = []
  for s1 in np2d.iter_contour_segments(c1.approx):
    if not segment_interesting(c1, c2, s1):
      continue
    for s2 in np2d.iter_contour_segments(c2.approx):
      if not segment_interesting(c1, c2, s2):
        continue
      # DO NOT SUBMIT: move 0.5 to constraints.
      gap_threshold = np2d.point_to_point_distance(c1.center, c2.center) * 0.5
      p_overlap = np2d.overlap(s1, s2, gap_threshold=gap_threshold)
      overlap_ok = p_overlap > .5  # DO NOT SUBMIT.
      if overlap_ok:
        result.append((s1, s2, p_overlap))
      # DO NOT SUBMIT.
      #else:
      #  study(s1, s2)
  return result


def _best_average_segment(
    segments: List[Tuple[np2d.Segment, np2d.Segment, float]],
) -> np2d.Segment:
  best_segment_index = -1
  best_score = -1
  for i, (_, _, score) in enumerate(segments):
    if score > best_score:
      best_score = score
      best_segment_index = i
  s1, s2, _ = segments[best_segment_index]
  s1p1, s1p2 = s1
  s2p1, s2p2 = s2
  if (np2d.point_to_point_distance(s1p1, s2p2) <
      np2d.point_to_point_distance(s1p1, s2p1)):
    # s1p1 is closer to s2p2; swap.
    s2p1, s2p2 = s2p2, s2p1
  return _midpoint(s1p1, s2p1), _midpoint(s1p2, s2p2)


def _midpoint(p1: np2d.Point, p2: np2d.Point) -> np2d.Point:
  x1, y1 = p1
  x2, y2 = p2
  return int(round((x1 + x2) / 2)), int(round((y1 + y2) / 2))


def segment_interesting(c1, c2, s):
  length = np2d.point_to_point_distance(*s)
  min_perimeter = min(c1.perimeter, c2.perimeter)
  if length / min_perimeter < .01:
    return False
  if not c1.convex or not c2.convex:
    return True
  return np2d.segments_intersect((c1.center, c2.center), s)



def n_siblings(hierarchy, start):
  count = 1
  next_sibling, previous_sibling, _, _ = hierarchy[start]
  while next_sibling >= 0:
    count += 1
    next_sibling, previous_sibling, _, _ = hierarchy[next_sibling]
    if next_sibling == start:
      break
  return count



def show_hierarchy(hierarchy, pos=0, indent=''):
  while pos != -1:
    next_sibling, previous_sibling, child, parent = hierarchy[pos]
    if child:
      siblings = n_siblings(hierarchy, child)
      if siblings > 1:
        siblings_suffix = ' (%d)' % siblings
      else:
        siblings_suffix = ''
    if next_sibling == -1:
      print_indent = indent.replace('├', '└')
    else:
      print_indent = indent
    print('%s─ %s%s' % (print_indent, pos, siblings_suffix))
    if child:
      show_hierarchy(hierarchy, pos=child, indent=indent.replace('├', '│')+'  ├')
    pos = next_sibling


_PADDING = 8


def study_contour(*contours, padding=_PADDING):
  """Studies contours."""
  colors = coloring.colors(len(contours))
  normalized = []
  for contour in contours:
    if len(contour.shape) > 2:
      size = contour.size
      contour = contour.view()
      contour.shape = (size // 2, 2)
    normalized.append(contour)
  contours = normalized
  min_x = min(c[:, 0].min() for c in contours) - padding
  min_y = min(c[:, 1].min() for c in contours) - padding
  max_x = max(c[:, 0].max() for c in contours) + padding - min_x
  max_y = max(c[:, 1].max() for c in contours) + padding - min_y
  move_to_zero = (-min_x, -min_y)
  image = np.zeros((max_y + 1, max_x + 1, 3), dtype=np.uint8)
  for contour, color in zip(contours, colors):
    #if len(contour) <= 1:
    #  continue
    contour.shape = (contour.size // 2, 1, 2)
    cv2.fillPoly(image, contour, color.tolist(), offset=move_to_zero)
  image = cv2.resize(image, None, fx=2, fy=2)
  show(image)


def bresenham_march(img, p1, p2):
  x1 = p1[0]
  y1 = p1[1]
  x2 = p2[0]
  y2 = p2[1]
  # tests if any coordinate is outside the image
  if (
      x1 >= img.shape[0]
      or x2 >= img.shape[0]
      or y1 >= img.shape[1]
      or y2 >= img.shape[1]
  ):  # tests if line is in image, necessary because some part of the line
    # must be inside, it respects the case that the two points are outside
    if not cv2.clipLine((0, 0, *img.shape), p1, p2):
      print("not in region")
      return

  steep = math.fabs(y2 - y1) > math.fabs(x2 - x1)
  if steep:
    x1, y1 = y1, x1
    x2, y2 = y2, x2

  # takes left to right
  also_steep = x1 > x2
  if also_steep:
    x1, x2 = x2, x1
    y1, y2 = y2, y1

  dx = x2 - x1
  dy = math.fabs(y2 - y1)
  error = 0.0
  delta_error = 0.0
  # Default if dx is zero
  if dx != 0:
    delta_error = math.fabs(dy / dx)

  y_step = 1 if y1 < y2 else -1

  y = y1
  ret = []
  for x in range(x1, x2):
    p = (y, x) if steep else (x, y)
    if p[0] < img.shape[0] and p[1] < img.shape[1]:
      ret.append((p, img[p]))
    error += delta_error
    if error >= 0.5:
      y += y_step
      error -= 1
  if also_steep:  # because we took the left to right instead
    ret.reverse()
  return ret

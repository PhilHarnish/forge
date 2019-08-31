import math
from typing import Tuple

import cv2
import numpy as np

from data.image import coloring, image, model
from puzzle.constraints.image import sliced_grid_constraints
from util.geometry import np2d


class SlicedGrid(object):
  _source: image.Image
  _constraints: sliced_grid_constraints.SlicedGridConstraints

  def __init__(
      self,
      source: image.Image,
      constraints: sliced_grid_constraints) -> None:
    self._source = source
    self._constraints = constraints

  def set_source(self, source: image.Image) -> None:
    self._source = source
    self._constraints.set_source(source)

  def get_slope_divisions(self) -> model.Divisions:
    c = self._constraints.center
    max_distance = sum(self._source.shape)
    for theta, distances, divisions in self._constraints.get_specs():
      endpoints = []
      total_distance = 0
      for distance in distances:
        moved = np2d.move_from(c, theta, distance)
        endpoints.append(moved)
        total_distance += abs(distance)
      start, end = endpoints
      division_distance = math.copysign(
          total_distance / divisions, -distances[0])
      right_angle = theta + math.pi / 2
      for i in range(0, divisions + 1):  # n_divisions requires n+1 iterations.
        x, y = np2d.move_from(start, theta, division_distance * i)
        dx = round(math.cos(right_angle) * max_distance)
        dy = round(math.sin(right_angle) * max_distance)
        yield (
          theta,
          (round(x - dx), round(y - dy)), (round(x + dx), round(y + dy)),
          i / divisions)

  def get_debug_data(self) -> Tuple[np.ndarray, np.ndarray, model.Divisions]:
    data = cv2.cvtColor(self._source.get_debug_data(), cv2.COLOR_GRAY2RGB)
    mask = np.zeros_like(data)
    c = self._constraints.center
    cv2.circle(data, c, 3, coloring.WHITE, thickness=3)
    cv2.circle(mask, c, 3, coloring.WHITE, thickness=3)
    for (theta, distances, divisions), color in zip(
        self._constraints.get_specs(),
        coloring.colors(self._constraints.slices)):
      for distance in distances:
        x, y = np2d.move_from(c, theta, distance)
        cv2.circle(data, (round(x), round(y)), 3, color, thickness=3)
    return data, mask, self.get_slope_divisions()

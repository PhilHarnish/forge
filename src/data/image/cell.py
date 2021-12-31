from typing import Set, Optional, Dict

import numpy as np

from data.image import edge, component, image

Neighbors = Dict['Cell', edge.Edge]


class Cell(component.PositionedComponent):
  _perimeter_points: np.ndarray
  _neighbors: Neighbors

  def __init__(
      self, source: np.ndarray, offset: component.Offset,
      perimeter_points: np.ndarray) -> None:
    super().__init__(source, offset)
    self._perimeter_points = perimeter_points
    self._neighbors = {}

  def neighbors(
      self, border: edge.Edge, neighbor: Optional['Cell']) -> Neighbors:
    if neighbor:
      self._neighbors[neighbor] = border
      neighbor._neighbors[self] = border
    return self._neighbors

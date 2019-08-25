from typing import Iterable, List, Tuple

import cv2
import numpy as np

from data.image import coloring, component, component_database, image, utils
from puzzle.constraints.image import decompose_constraints
from puzzle.steps.image import _base_image_step

_IGNORED_SYMBOLS = {
  'FULL_CIRCLE',  # TODO: Detect and handle geometric shapes differently.
}
_SYMBOL_MAP = {
  'UP_ARROW': '^',
  'DOWN_ARROW': 'v',
  'LEFT_ARROW': '<',
  'RIGHT_ARROW': '>',
  'ADD': '+',
  'MULTIPLY': 'x',
  'DIVIDE': '/',
}


class Decompose(_base_image_step.BaseImageStep):
  _decompose_constraints: decompose_constraints.DecomposeConstraints
  _prepare_image_step: _base_image_step.BaseImageStep
  _components: List[component.Component]
  _database: component_database.ComponentDatabase

  def __init__(
      self,
      prepare_image_step: _base_image_step.BaseImageStep,
      constraints: decompose_constraints.DecomposeConstraints) -> None:
    super(Decompose, self).__init__(
        prepare_image_step.get_result(),
        dependencies=[prepare_image_step],
        constraints=[constraints])
    self._prepare_image_step = prepare_image_step
    self._prepare_image_step.subscribe(self._on_constraints_changed)
    self._decompose_constraints = constraints
    self._components = []
    self._database = component_database.ComponentDatabase()

  def get_debug_data(self) -> np.ndarray:
    data = cv2.cvtColor(self.get_result().get_debug_data(), cv2.COLOR_GRAY2RGB)
    for c in self._components:
      symbol = c.labels.get('symbol')
      top, left = c.offset
      if symbol and symbol not in _IGNORED_SYMBOLS:
        symbol = _SYMBOL_MAP.get(symbol, symbol)
        height, width = c.image.shape[:2]
        size = height / 18
        x, y = left - 5, top + height
        cv2.putText(
            data, symbol, (x, y), cv2.FONT_HERSHEY_SIMPLEX, size, (255, 0, 0))
    return data

  def get_components(self) -> Iterable[component.Component]:
    # Ensure result has been created.
    self.get_result()
    yield from self._components

  def _get_new_source(self) -> image.Image:
    return self._prepare_image_step.get_result().fork()

  def _modify_result(self, result: image.Image) -> image.Image:
    constraints = self._decompose_constraints
    for band, targeted, opened in _significant_color_bands(
        result, constraints.required_color_band_retention):
      for c in _components_for_image(targeted):
        self._database.identify(c)
        self._components.append(c)
        symbol = c.labels.get('symbol')
        if symbol and symbol not in _IGNORED_SYMBOLS:
          result.erase_component(
              c,
              constraints.erase_border_percentile,
              constraints.erase_border_distance,
              constraints.erase_border_size)
    return result


def _significant_color_bands(
    src: image.Image,
    required_color_band_retention: float,
) -> Iterable[Tuple[coloring.ColorBand, np.ndarray, np.ndarray]]:
  """Returns the best guess at "significant" colors which have information."""
  batches = reversed(list(coloring.top_n_color_clusters(src.bincount, 6)))
  for batch in batches:
    low, high = batch[0], batch[-1]
    targeted = src.color_band(low, high)
    targeted_count = np.count_nonzero(targeted)
    if not targeted_count:
      continue  # This can happen if previously prominent colors were erased.
    opened = utils.morph_open(targeted)
    opened_count = np.count_nonzero(opened)
    if opened_count / targeted_count < required_color_band_retention:
      continue  # Too much erosion; original prominence likely due to antialias.
    yield (low, high), targeted, opened


def _components_for_image(src: np.ndarray) -> Iterable[component.Component]:
  # TODO: This needs to be cleaned up. It should use constraints instead of
  # constants.
  n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(src)
  height, width = labels.shape
  total_area = width * height
  max_allowed_area = int(total_area * 0.05)
  min_allowed_area = 8
  max_allowed_area_ratio = .9
  min_allowed_dimension = min(width, height) * .01  # Max 100 symbols/row.
  for i in range(n_labels):
    area = stats[i, cv2.CC_STAT_AREA]
    if area > max_allowed_area or area < min_allowed_area:
      continue  # Too big compared to overall image.
    left = stats[i, cv2.CC_STAT_LEFT]
    top = stats[i, cv2.CC_STAT_TOP]
    width = stats[i, cv2.CC_STAT_WIDTH]
    height = stats[i, cv2.CC_STAT_HEIGHT]
    if (width > min_allowed_dimension and  # Special exception for | shapes.
        area > (width * height * max_allowed_area_ratio)):
      continue  # Too dense (e.g. full square block).
    elif (
        height < min_allowed_dimension or
        min(width, height) < 2):
      continue
    cropped = labels[top:top + height, left:left + width]
    selected = np.where(
        cropped == i, coloring.MAX_BROADCAST, coloring.MIN_BROADCAST)
    offset = component.Offset(top, left)
    yield component.Component(selected, offset=offset)

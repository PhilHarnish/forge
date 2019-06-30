import itertools
from typing import Iterable, Tuple

import cv2
import numpy as np

from data import lazy
from data.image import component, component_database, utils

_MAX = 255
_WHITE = [_MAX, _MAX, _MAX]
_THRESHOLD = 5
_SIZES = []
pos = 16
for backwards in range(-1, -11, -1):
  for _ in range(0, 8):
    _SIZES.append(pos)
    pos += 1
  _SIZES.append(16 + backwards)


class Grid(object):
  def __init__(self, cv_image: np.ndarray) -> None:
    self._original = utils.crop(_normalize(cv_image), _WHITE)

  @lazy.prop
  def threshold(self) -> np.ndarray:
    result = cv2.adaptiveThreshold(
        self.grayscale, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv2.THRESH_BINARY_INV, blockSize=11, C=15)
    return cv2.dilate(result, self._cross, iterations=1)

  @lazy.prop
  def _grayscale(self) -> np.ndarray:
    return cv2.cvtColor(self._original, cv2.COLOR_BGR2GRAY)

  @lazy.prop
  def grayscale(self) -> np.ndarray:
    scaled = self._grayscale
    # Some images are dim.
    # TODO: This normalization should happen even earlier.
    counts = self._grayscale_bincount
    interesting_threshold = int(counts.max() * .001)
    darkest = 0
    while counts[darkest] < interesting_threshold:
      darkest += 1
    brightest = len(counts) - 1
    while counts[brightest] < interesting_threshold:
      brightest -= 1
    if darkest:
      # If the first "darkest" color with nontrivial count is nonzero then shift
      # down.
      scaled -= darkest
    current_range = brightest - darkest
    if current_range < _MAX:
      # If less than the entire spectrum is used (255), scale.
      # E.g.: 3 / 4 -> 4 / 4 == 3 * x = 4 == x = 4 / 3.
      factor = _MAX / current_range
      scaled = np.multiply(scaled, factor, out=scaled, casting='unsafe')
    return scaled

  @lazy.prop
  def grayscale_inv(self) -> np.ndarray:
    return cv2.bitwise_not(self.grayscale)

  @lazy.prop
  def grid_with_components(self) -> np.ndarray:
    grayscale = self.grayscale_inv
    for mask, color in self._layer_masks():
      grayscale = np.where(mask == 0, grayscale, color)
    return cv2.threshold(
        grayscale, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

  @lazy.prop
  def grid_with_components_inv(self) -> np.ndarray:
    grayscale = self.grayscale_inv
    for mask, color in self._layer_masks():
      grayscale = np.where(mask == 0, grayscale, color)
    return cv2.threshold(
        grayscale, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

  @lazy.prop
  def grid(self) -> np.ndarray:
    # TODO: Keep metadata on component positions.
    grayscale = self.grayscale_inv
    for mask, color in itertools.chain(
        self._layer_masks(), self._component_masks(include_inverted=True)):
      grayscale = np.where(mask == 0, grayscale, color)
    inv = cv2.bitwise_not(grayscale)
    return cv2.adaptiveThreshold(
        inv, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv2.THRESH_BINARY_INV, blockSize=11, C=15)

  @lazy.prop
  def components(self) -> Iterable[component.Component]:
    for c, _ in self._components_with_source(include_inverted=True):
      yield c

  @lazy.prop
  def _cross(self) -> np.ndarray:
    src = self._original
    size = int(max(src.shape) * .0025)
    if size < 3:
      size = 3
    elif size % 2 == 0:
      size += 1
    cross = np.zeros((size, size), np.uint8)
    for x in range(size):
      middle = (size - 1) >> 1
      cross[middle][x] = 1
      cross[x][middle] = 1
    return cross

  def _components_with_source(
      self,
      include_inverted: bool = False
  ) -> Iterable[Tuple[component.Component, np.ndarray]]:
    yield from _components_with_source_for_image(
        self.grid_with_components, inverted=False)
    if include_inverted:
      yield from _components_with_source_for_image(
          cv2.bitwise_not(self.grid_with_components_inv), inverted=True)

  def _component_masks(
      self, include_inverted: bool = False) -> Iterable[Tuple[np.ndarray, int]]:
    db = component_database.ComponentDatabase()
    for c, src in self._components_with_source(
        include_inverted=include_inverted):
      identified = db.identify(c)
      symbol = identified.labels.get('symbol')
      if symbol:
        if c.labels.get('inverted'):
          color = _MAX
        else:
          color = 0
        yield cv2.dilate(src, self._cross, iterations=1), color

  @lazy.prop
  def _grayscale_bincount(self) -> np.ndarray:
    return np.bincount(self._grayscale.ravel())

  @lazy.prop
  def _grayscale_inv_bincount(self) -> np.ndarray:
    return np.bincount(self.grayscale_inv.ravel())

  def _layer_masks(self, n: int = 5) -> Iterable[Tuple[np.ndarray, int]]:
    counts = self._grayscale_inv_bincount
    top_n = list(range(-1, -n, -1))
    partitioned = np.argpartition(counts, top_n)
    grayscale = self.grayscale_inv
    for i in top_n:
      target = partitioned[i]
      if target > (_MAX - _THRESHOLD) or target < _THRESHOLD:
        continue
      targeted = np.where(grayscale == target, grayscale, 0)
      # Erode and then over-dilate to eliminate noise.
      morphed = cv2.dilate(
          cv2.erode(targeted, self._cross, iterations=1),
          self._cross,
          iterations=2)
      if not morphed.any():
        continue  # Nothing left after eroded.
      reselected = np.where(targeted == morphed, targeted, 0)
      yield reselected, 0


def _normalize(src: np.ndarray) -> np.ndarray:
  if len(src.shape) == 2:  # BW.
    result = np.zeros((src.shape[0], src.shape[1], 3), dtype=src.dtype)
    result[:, :, 0] = src
    result[:, :, 1] = src
    result[:, :, 2] = src
    return result
  elif len(src.shape) != 3:
    raise ValueError('Unsupported shape %s' % src.shape)
  n_channels = src.shape[-1]
  if n_channels == 3:  # RGB.
    return src
  elif n_channels != 4:  # RGBA.
    raise ValueError('Unsupported number of channels %s' % n_channels)
  # Make transparent pixels white.
  for row in src:
    for col in row:
      if not col[3]:
        col[0], col[1], col[2] = 255, 255, 255
  return cv2.cvtColor(src, cv2.COLOR_BGRA2BGR)


def _components_with_source_for_image(
    image: np.ndarray,
    inverted: bool = False
) -> Iterable[Tuple[component.Component, np.ndarray]]:
  n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
  width, height = labels.shape
  total_area = width * height
  max_allowed_area = int(total_area * 0.05)
  min_allowed_area = 8
  max_allowed_area_ratio = .9
  min_allowed_dimension = min(width, height) * .01  # Max 100 symbols/row.
  max_allowed_dimension = max(width, height) * .10  # Min 10 symbols/row.
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
    elif (max(width, height) > max_allowed_dimension or
        height < min_allowed_dimension or
        min(width, height) < 2):
      continue
    selected = np.where(labels == i, image, 0)
    cropped = selected[top:top + height, left:left + width]
    if inverted:
      component_labels = {'inverted': True}
    else:
      component_labels = None
    yield component.Component(cropped, labels=component_labels), selected

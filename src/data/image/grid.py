import itertools
from typing import Iterable, Tuple

import cv2
import numpy as np

from data import lazy
from data.image import coloring, component, component_database, utils

_MAX = 255
_WHITE = [_MAX, _MAX, _MAX]
_THRESHOLD = 5


class Grid(object):
  def __init__(self, cv_image: np.ndarray) -> None:
    self._original = utils.crop(coloring.normalize(cv_image), _WHITE)

  @lazy.prop
  def grayscale_inv(self) -> np.ndarray:
    inverted = cv2.bitwise_not(cv2.cvtColor(self._original, cv2.COLOR_BGR2GRAY))
    return coloring.enhance(inverted, out=inverted)

  @lazy.prop
  def grid_with_components(self) -> np.ndarray:
    grayscale = self.grayscale_inv
    for mask, color in self._layer_masks():
      grayscale = np.where(mask == 0, grayscale, color)
    return cv2.threshold(
        grayscale, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

  @lazy.prop
  def grid_without_threshold(self) -> np.ndarray:
    # TODO: Keep metadata on component positions.
    grayscale = np.copy(self.grayscale_inv)
    for mask, color in itertools.chain(
        self._layer_masks(), self._component_masks(include_inverted=True)):
      if color == 0:
        weight = -1
      else:
        weight = 1
      cv2.addWeighted(grayscale, 1, utils.antialias(mask), weight, 0, dst=grayscale)
    return grayscale

  @lazy.prop
  def grid(self) -> np.ndarray:
    src = np.array(np.where(self.grid_without_threshold > _THRESHOLD, _MAX, 0), dtype=np.uint8)
    return utils.preserve_stroke(src, _MAX, .9)

  @lazy.prop
  def components(self) -> Iterable[component.Component]:
    for c, _ in self._components_with_source(include_inverted=True):
      yield c

  def _components_with_source(
      self,
      include_inverted: bool = False
  ) -> Iterable[Tuple[component.Component, np.ndarray]]:
    yield from _components_with_source_for_image(
        self.grid_with_components, inverted=False)
    if include_inverted:
      yield from _components_with_source_for_image(
          cv2.bitwise_not(self.grid_with_components), inverted=True)

  def _component_masks(
      self, include_inverted: bool = False) -> Iterable[Tuple[np.ndarray, int]]:
    db = component_database.ComponentDatabase()
    for c, src in self._components_with_source(
        include_inverted=include_inverted):
      db.identify(c)
      symbol = c.labels.get('symbol')
      if symbol:
        if c.labels.get('inverted'):
          color = _MAX
        else:
          color = 0
        yield src, color

  @lazy.prop
  def _grayscale_inv_bincount(self) -> np.ndarray:
    return np.bincount(self.grayscale_inv.ravel())

  def _layer_masks(self, n: int = 6, show = lambda *x: None) -> Iterable[Tuple[np.ndarray, int]]:
    src = self.grayscale_inv
    show(src)
    # DO NOT SUBMIT: "show" param.
    batches = list(reversed(list(
        coloring.top_n_color_clusters(self._grayscale_inv_bincount, n))))
    print(batches)
    kernel_size = 5
    kernel = utils.kernel_circle(kernel_size)
    # Normalized kernal used during blurring. Multiply 2x to intensify.
    kernel_normalized = 2 * kernel / np.count_nonzero(kernel)
    forbidden_zone = np.zeros_like(src)
    blocked_next = forbidden_zone
    for batch in batches:
      low, high = batch[0] - _THRESHOLD, batch[-1] + _THRESHOLD
      targeted = np.where(((low < src) & (src < high)), src, 0)
      blocked_count = np.count_nonzero((targeted != 0) & (blocked_next != 0))
      print('blocked count:', blocked_count, 100 * blocked_count / src.size)
      if low > 0 and high < _MAX:
        print('targeted batch %s [%s, %s] (%s)' % (batch, low, high, kernel_size))
        show(targeted)
        show('brighter', np.where(src > high, 255, 0))
        # WARNING: 1.75 is very finely tuned. Any lower and grid lines are
        # removed.
        opened = utils.preserve_stroke(targeted, low, 1.75)
        if not np.any(opened):
          continue
        #opened_percent = 100 * np.count_nonzero(targeted) / opened.size
        #if opened_percent < 1: continue
        #print('opened %.02f' % opened_percent)
        show('opened', opened)
        yield opened, 0
        if show:
          blurred = cv2.filter2D(
              opened,
              cv2.CV_8UC1,
              kernel_normalized,
              borderType=cv2.BORDER_ISOLATED)
          print('blurred')
          show(blurred)
          subtracted = src - blurred
          result = np.array(np.where(src < blurred, 0, subtracted), dtype=np.uint8)
          show('result', result)
          show('nonzero', np.array(np.where(result > 0, 255, 0), dtype=np.uint8))
      # Mark more territory as forbidden.
      np.maximum(forbidden_zone, targeted, out=forbidden_zone)
      blocked_next = cv2.dilate(forbidden_zone, kernel, iterations=2)
      show('blocked_next', blocked_next)


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

import collections
import typing

import cv2
import numpy as np

from data import lazy
from data.image import coloring

_CROSS = np.array([
  [0, 1, 0],
  [1, 1, 1],
  [0, 1, 0],
], np.uint8)


class Grid(object):
  def __init__(self, cv_image: np.ndarray) -> None:
    self._original = _normalize(cv_image)
    self._scratch = np.copy(self._original)

  @lazy.prop
  def threshold(self) -> np.ndarray:
    result = cv2.adaptiveThreshold(
        self.grayscale, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv2.THRESH_BINARY_INV, blockSize=11, C=15)
    return cv2.dilate(result, _CROSS, iterations=1)

  @lazy.prop
  def grayscale(self) -> np.ndarray:
    return cv2.cvtColor(self._original, cv2.COLOR_BGR2GRAY)

  @lazy.prop
  def with_components(self) -> np.ndarray:
    output = np.copy(self._original)
    n_labels, labels, stats, centroids = self._components
    return coloring.color_components(n_labels, output, labels, stats)

  @lazy.prop
  def with_largest_component(self) -> np.ndarray:
    output = np.copy(self._original)
    n_labels, labels, stats, centroids = self._components
    return coloring.color_components(2, output, labels, stats)

  @lazy.prop
  def with_lines(self) -> np.ndarray:
    output = np.copy(self._original)
    for rho, theta in self._hough_lines:
      a = np.cos(theta)
      b = np.sin(theta)
      x0 = a * rho
      y0 = b * rho
      x1 = int(x0 + 5000 * -b)
      y1 = int(y0 + 5000 * a)
      x2 = int(x0 - 5000 * -b)
      y2 = int(y0 - 5000 * a)

      cv2.line(output, (x1, y1), (x2, y2), (255, 0, 0, 255), thickness=1)

    for rho, theta in self._grid_lines:
      a = np.cos(theta)
      b = np.sin(theta)
      x0 = a * rho
      y0 = b * rho
      x1 = int(x0 + 5000 * -b)
      y1 = int(y0 + 5000 * a)
      x2 = int(x0 - 5000 * -b)
      y2 = int(y0 - 5000 * a)

      cv2.line(output, (x1, y1), (x2, y2), (0, 0, 255, 255), thickness=2)
    return output

  @lazy.prop
  def _components(
      self) -> typing.Tuple[int, np.ndarray, np.ndarray, np.ndarray]:
    return cv2.connectedComponentsWithStats(self.threshold)

  @lazy.prop
  def _hough_lines(self) -> typing.List[typing.Tuple[float, float]]:
    edges = cv2.Canny(self.threshold, 50, 150, apertureSize=3)
    hough_lines = []
    cv_hough_lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    if cv_hough_lines is None:
      return []
    for line in cv_hough_lines:
      for rho, theta in line:
        hough_lines.append((rho, theta))
    return sorted(hough_lines, key=lambda x: x[0])

  @lazy.prop
  def _grid_lines(self) -> typing.List[typing.Tuple[float, float]]:
    horizontal_lines = []
    vertical_lines = []
    for rho, theta in self._hough_lines:
      clamped_theta = (round(10 * theta / np.pi) % 10) / 10
      if rho < 0:
        continue  # TODO: Do real math to find where this line enters image.
      if clamped_theta == 0.5:
        # Horizontal.
        horizontal_lines.append((rho, theta))
      elif clamped_theta == 0.0:
        # Vertical.
        vertical_lines.append((rho, theta))
      else:
        # TODO: Actually measure "askew" instead of clamping.
        print('theta is too askew: %s' % theta)
        continue
    horizontal_threshold = _gap_threshold([rho for rho, _ in horizontal_lines])
    vertical_threshold = _gap_threshold([rho for rho, _ in vertical_lines])

    return (_threshold_lines(horizontal_lines, horizontal_threshold) +
            _threshold_lines(vertical_lines, vertical_threshold))


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


def _gap_threshold(rhos: typing.List[int]) -> int:
  if not rhos:
    return 0
  extent = rhos[-1] - rhos[0]
  n_squares_guess = collections.Counter()
  for left, right in zip(rhos, rhos[1:]):
    delta = right - left
    n_squares = int(extent / delta)
    if n_squares > 100:
      continue
    n_squares_guess[n_squares] += 1
  if not n_squares_guess:
    return 0
  freq_dist = n_squares_guess.most_common()  # Freq, ordered most -> least.
  largest_n_guess = freq_dist[0][0]
  # Look for the "largest" number that touches the "most common".
  while n_squares_guess[largest_n_guess + 1]:
    largest_n_guess += 1
  return int(extent / largest_n_guess)


def _threshold_lines(
    lines: typing.List[typing.Tuple[float, float]],
    threshold: float,
) -> typing.List[typing.Tuple[float, float]]:
  right_edge = float('-inf')
  bucket = []
  buckets = [bucket]
  for rho, theta in lines:
    if rho > right_edge:
      right_edge = rho + threshold
      bucket = []
      buckets.append(bucket)
    bucket.append((rho, theta))
  result = []
  for bucket in buckets:
    if not bucket:
      continue
    average_rho = sum(rho for rho, _ in bucket) / len(bucket)
    average_theta = sum(theta for _, theta in bucket) / len(bucket)
    result.append((average_rho, average_theta))
  return result

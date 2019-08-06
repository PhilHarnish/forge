import colorsys
from typing import Iterable, List, Optional

import cv2
import numpy as np

from util import perf

MIN = 0
MAX = 255
MIN_BROADCAST = np.array([MIN], dtype=np.uint8)
MAX_BROADCAST = np.array([MAX], dtype=np.uint8)
_MAX_ENHANCE_DISTANCE = 64
_MAX_COLORS_PER_HLS_SLICE = 7
_THRESHOLD = 5
_BLACK = np.array([0, 0, 0], dtype=np.uint8)
_WHITE = np.array([MAX, MAX, MAX], dtype=np.uint8)


p = perf.Perf('enhance', ['cv2', 'oldschool'])


def colors(n: int, with_black_and_white=False) -> Iterable[np.ndarray]:
  """Returns n (or more) colors."""
  if with_black_and_white:
    n -= 2
    yield _BLACK
    yield _WHITE
  if n <= 0:
    return
  n_slices = int(n / _MAX_COLORS_PER_HLS_SLICE) + 1
  lightness_scale = 0.25  # 50% +/- 25%.
  for slice_n in range(n_slices):
    n_colors_in_slice = min(n, _MAX_COLORS_PER_HLS_SLICE)
    if slice_n % 2:
      offset = 1 / (2 * n_colors_in_slice)
    else:
      offset = 0
    for color in range(n_colors_in_slice):
      hue = (color / n_colors_in_slice) + offset
      lightness = .5 + lightness_scale * (slice_n / n_slices)
      saturation = 1.0
      r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
      yield np.array(
          [int(r * 255), int(g * 255), int(b * 255)], dtype=np.uint8)
    n -= _MAX_COLORS_PER_HLS_SLICE
    lightness_scale *= -1


def color_band(
    src: np.ndarray, low: int, high: Optional[int] = None) -> np.ndarray:
  if high is None or low == high:
    return np.where(src == low, MAX_BROADCAST, MIN_BROADCAST)
  return np.where(
      ((low <= src) & (src <= high)), MAX_BROADCAST, MIN_BROADCAST)


def enhance(src: np.ndarray, out: np.ndarray = None) -> np.ndarray:
  if src.dtype != np.uint8:
    raise NotImplementedError('enhance() only supports uint8')
  nonzero = src[src != 0]
  if not nonzero.size:
    return src
  lowest, highest = np.percentile(nonzero, (1, 90), interpolation='lower')
  # NB: np.percentile() returns ndarray which confuses addWeighted.
  lowest = min(int(lowest), _MAX_ENHANCE_DISTANCE)
  highest = max(int(highest), MAX - _MAX_ENHANCE_DISTANCE)
  current_range = highest - lowest
  if not current_range:
    return np.add(src, MAX - lowest, out=out, dtype=np.uint8)
  elif current_range == MAX:
    return np.array(src, dtype=np.uint8)
  # If less than the entire spectrum is used (255), scale to fit.
  # E.g.: 3 / 4 -> 4 / 4 == 3 * x = 4 == x = 4 / 3.
  factor = MAX / current_range
  # cv2.addWeighted is >5x faster than `a = m*x + b` style.
  return cv2.addWeighted(src, factor, 0, 0, -int(lowest), dst=out)


def normalize(src: np.ndarray) -> np.ndarray:
  if len(src.shape) == 2:  # Monochrome.
    height, width = src.shape
    result = np.zeros((height, width, 3), dtype=np.uint8)
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
  # Make any pixel with 0 alpha chanel white.
  src[src[:,:,3] == 0] = 255
  return cv2.cvtColor(src, cv2.COLOR_BGRA2BGR)


def top_n_color_clusters(
    counts: np.ndarray, n: int, threshold: int = _THRESHOLD
) -> Iterable[List[int]]:
  """Given a histogram of counts, cluster and return top N values."""
  max_value = len(counts)
  if not max_value:
    return
  top_n = list(range(max_value - 1, max_value - n - 1, -1))
  partitioned = np.argpartition(counts, top_n)
  batch = []
  last = None
  positions = []
  for i in top_n:
    if (counts[partitioned[i]] and
        threshold < partitioned[i] < (max_value - threshold)):
      positions.append(partitioned[i])
  # TODO: positions = [partitioned[i] for i in top_n]
  for position in sorted(positions):
    if last is not None and abs(last - position) > threshold:
      yield batch
      # Start a new batch.
      batch = []
    batch.append(position)
    last = position
  if batch:
    yield batch

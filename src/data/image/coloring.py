import colorsys
from typing import List

import cv2
import numpy as np

_MAX_COLORS_PER_HLS_SLICE = 7
_BLACK = np.fromiter([0, 0, 0], dtype=np.int32)
_WHITE = np.fromiter([255, 255, 255], dtype=np.int32)


def color_components(
    n_components: int, result: np.ndarray, labels: np.ndarray,
    stats: np.ndarray) -> np.ndarray:
  """Colors n largest components."""
  n_stats = stats.shape[0]
  color_list = colors(n_stats, with_black_and_white=True)
  sizes_sorted = sorted(
      list(range(n_stats)),
      key=lambda i: stats[i, cv2.CC_STAT_AREA],
      reverse=True)
  # Invert sizes_sorted array to produce a color map.
  color_map = [0] * len(sizes_sorted)
  for idx, i in enumerate(sizes_sorted):
    color_map[i] = idx
  height, width = labels.shape
  for y in range(height):
    for x in range(width):
      color_idx = color_map[labels[y, x]]
      if color_idx >= n_components:
        color_idx = 0  # Erase this component to leave only n_components.
      color = color_list[color_idx]
      result[y, x] = color
  return result


def colors(n: int, with_black_and_white=False) -> List[np.ndarray]:
  """Returns n (or more) colors."""
  if with_black_and_white:
    result = [_BLACK, _WHITE]
  else:
    result = []
  n -= len(result)
  if n <= 0:
    return result
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
      result.append(
          np.fromiter(
              [int(r * 255), int(g * 255), int(b * 255)], dtype=np.uint8))
    n -= _MAX_COLORS_PER_HLS_SLICE
    lightness_scale *= -1
  return result

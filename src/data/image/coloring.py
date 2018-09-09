import colorsys
import typing

import cv2
import numpy as np

_MAX_COLORS_PER_HLS_SLICE = 7


def color_components(
    n_components: int, result: np.ndarray, labels: np.ndarray,
    stats: np.ndarray) -> np.ndarray:
  colors = _colors(n_components, result.dtype)
  sizes_sorted = sorted(
      list(range(n_components)),
      key=lambda i: stats[i, cv2.CC_STAT_AREA],
      reverse=True)
  # Invert sizes_sorted array to produce a color map.
  color_map = [0] * n_components
  for idx, i in enumerate(sizes_sorted):
    color_map[i] = idx
  height, width = labels.shape
  for y in range(height):
    for x in range(width):
      color = colors[color_map[labels[y, x]]]
      result[y, x] = color
  return result


def _colors(n: int, dtype: np.dtype) -> typing.List[np.ndarray]:
  if not n:
    return []
  result = [
    np.fromiter([0, 0, 0], dtype=dtype),
  ]
  if n == 1:
    return result
  result.append(np.fromiter([255, 255, 255], dtype=dtype))
  n -= 2
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
          np.fromiter([int(r * 255), int(g * 255), int(b * 255)], dtype=dtype))
    n -= _MAX_COLORS_PER_HLS_SLICE
    lightness_scale *= -1
  return result

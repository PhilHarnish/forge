import colorsys
from typing import Iterable, List

import numpy as np

_MAX_COLORS_PER_HLS_SLICE = 7
_MAX = 255
_THRESHOLD = 5
_BLACK = np.array([0, 0, 0], dtype=np.uint8)
_WHITE = np.array([_MAX, _MAX, _MAX], dtype=np.uint8)


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
  for position in sorted(positions):
    if last and abs(last - position) > threshold:
      yield batch
      # Start a new batch.
      batch = []
    batch.append(position)
    last = position
  if batch:
    yield batch

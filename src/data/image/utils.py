from typing import List, Tuple, Union

import cv2
import numpy as np

from data.image import coloring


def antialias(src: np.ndarray) -> np.ndarray:
  return cv2.dilate(src, _ANTIALIAS_KERNEL, iterations=2)


def crop(
    src: np.ndarray, ignore: Union[int, List[int], np.ndarray]) -> np.ndarray:
  for _ in range(2):
    while np.all(src[0] == ignore):
      src = src[1:]
    while np.all(src[-1] == ignore):
      src = src[:-1]
    src = np.swapaxes(src, 0, 1)  # Swap x/y axis.
  return src


def kernel_circle(size: int) -> np.ndarray:
  radius = size // 2
  # Create a slice which centers cursor at origin.
  y, x = np.ogrid[-radius:radius + 1, -radius:radius + 1]
  mask = x ** 2 + y ** 2 <= radius ** 2
  array = np.zeros((size, size), np.uint8)
  array[mask] = 1
  return array


def kernel_cross(size: int) -> np.ndarray:
  array = np.zeros((size, size), np.uint8)
  for x in range(size):
    middle = (size - 1) >> 1  # int(size / 2).
    array[middle][x] = 1
    array[x][middle] = 1
  return array


def morph_open(src: np.ndarray) -> np.ndarray:
  return cv2.morphologyEx(src, cv2.MORPH_OPEN, _OPEN_KERNEL)


def outline_and_fill(
    src: np.ndarray, distance: int, size: int) -> Tuple[np.ndarray, np.ndarray]:
  """Expand `src` `distance`; return outline which extends further by `size`."""
  if distance:
    expanded_inner = cv2.dilate(src, _SMALL_KERNEL, iterations=distance)
  else:
    expanded_inner = src
  expanded_outer = cv2.dilate(expanded_inner, _SMALL_KERNEL, iterations=size)
  return np.where(
      expanded_inner != expanded_outer,
      coloring.MAX_BROADCAST,
      coloring.MIN_BROADCAST), expanded_outer


def preserve_stroke(
    src: np.ndarray, threshold: int, thickness: float) -> np.ndarray:
  """Maintains strokes >= `threshold` brightness and `thickness` width."""
  min_pixels = int(threshold * _STROKE_KERNEL_SIZE * thickness)
  filtered = cv2.filter2D(
      src,
      cv2.CV_8UC1,
      _STROKE_KERNEL,
      delta=-min_pixels,
      borderType=cv2.BORDER_ISOLATED)
  return np.where(filtered > _THRESHOLD, src, 0)


_SMALL_KERNEL = kernel_circle(3)
_ANTIALIAS_KERNEL = _SMALL_KERNEL
_OPEN_KERNEL = kernel_circle(3)
_STROKE_KERNEL_SIZE = 5
_STROKE_KERNEL = kernel_circle(_STROKE_KERNEL_SIZE)
_THRESHOLD = 5

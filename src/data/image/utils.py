from typing import List, Union

import numpy as np


def crop(
    src: np.ndarray, ignore: Union[int, List[int], np.ndarray]) -> np.ndarray:
  while np.all(src[0] == ignore):
    src = src[1:]
  while np.all(src[-1] == ignore):
    src = src[:-1]
  src = np.swapaxes(src, 0, 1)  # Swap x/y axis.
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
    middle = (size - 1) >> 1
    array[middle][x] = 1
    array[x][middle] = 1
  return array

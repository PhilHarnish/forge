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

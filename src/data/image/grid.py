import cv2
import numpy as np

from data import lazy


class Grid(object):
  def __init__(self, cv_image: np.ndarray) -> None:
    self._cv_image = _normalize(cv_image)

  @lazy.prop
  def grayscale(self) -> np.ndarray:
    return cv2.cvtColor(self._cv_image, cv2.COLOR_BGR2GRAY)


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
  return src

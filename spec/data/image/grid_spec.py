import glob
import os
from os import path

import cv2
import numpy as np
from PIL import Image

from data import data
from data.image import grid
from spec.mamba import *

_FILE_PATTERN = '*.png'


def image_path(pattern: str, subdir: str = 'original') -> Iterator[np.ndarray]:
  return path.join(data.project_path('data/grid'), subdir, pattern)


def images(subdir: str = 'original') -> Iterator[np.ndarray]:
  for filename in glob.glob(image_path(_FILE_PATTERN, subdir)):
    yield (
      path.basename(filename),
      cv2.imread(filename, flags=cv2.IMREAD_UNCHANGED))


def diff_property(prop: str) -> None:
  for name, image in images():
    os.makedirs(path.join(data.project_path('data/grid'), prop), exist_ok=True)
    Image.fromarray(getattr(grid.Grid(image), prop)).save(
        image_path(name, prop))
    # TODO: Diff.


with description('grid'):
  with it('grayscale'):
    diff_property('grayscale')

  with it('threshold'):
    diff_property('threshold')

  with it('with_components'):
    diff_property('with_components')

  with it('with_largest_component'):
    diff_property('with_largest_component')

  with it('with_lines'):
    diff_property('with_lines')

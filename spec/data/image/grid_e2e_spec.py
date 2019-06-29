import glob
import os
from os import path

import cv2
import numpy as np
from PIL import Image

from data import data, warehouse
from data.image import grid
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

_FILE_PATTERN = '*.png'
_FOCUS = {
}


def image_path(pattern: str, subdir: str = 'original') -> str:
  return path.join(data.project_path('data/grid'), subdir, pattern)


def images(subdir: str = 'original') -> Iterator[np.ndarray]:
  for filename in sorted(glob.glob(image_path(_FILE_PATTERN, subdir))):
    yield (
      path.basename(filename),
      cv2.imread(filename, flags=cv2.IMREAD_UNCHANGED))


def grids(subdir: str = 'original') -> Iterator[Tuple[str, grid.Grid]]:
  for name, image in images(subdir):
    if _FOCUS and name not in _FOCUS:
      continue
    yield name, grid.Grid(image)


def diff_property(prop: str) -> None:
  for name, grid in grids():
    os.makedirs(path.join(data.project_path('data/grid'), prop), exist_ok=True)
    Image.fromarray(getattr(grid, prop)).save(
        image_path(name, prop))
    # TODO: Diff.


with description('grid', 'end2end') as self:
  with before.all:
    warehouse.save()
    prod_config.init()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('diffs grayscale'):
    with benchmark(2500):
      diff_property('grayscale')

  with it('diffs grid'):
    with benchmark(2100):
      diff_property('grid')

  with it('diffs threshold'):
    with benchmark(2400):
      diff_property('threshold')

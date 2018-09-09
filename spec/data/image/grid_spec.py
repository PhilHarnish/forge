import glob
import os
from os import path

import cv2
import numpy as np
from PIL import Image

from data import data
from data.image import grid
from spec.mamba import *


def image_path(name: str, subdir: str = 'original') -> Iterator[np.ndarray]:
  return path.join(data.project_path('data/grid'), subdir, '%s.png' % name)


def images(subdir: str = 'original') -> Iterator[np.ndarray]:
  for filename in glob.glob(image_path('*', subdir)):
    yield (
      path.splitext(path.basename(filename)),
      cv2.imread(filename, flags=cv2.IMREAD_UNCHANGED))


def diff_property(prop: str) -> None:
  for (base, ext), image in images():
    os.makedirs(path.join(data.project_path('data/grid'), prop), exist_ok=True)
    Image.fromarray(getattr(grid.Grid(image), prop)).save(
        image_path('%s.actual' % base, prop))
    # TODO: Diff.


with description('grid'):
  with it('grayscale'):
    diff_property('grayscale')

  with it('threshold'):
    diff_property('threshold')

  with it('with_lines'):
    diff_property('with_lines')

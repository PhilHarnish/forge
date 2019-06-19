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


def image_path(pattern: str, subdir: str = 'original') -> str:
  return path.join(data.project_path('data/grid'), subdir, pattern)


def images(subdir: str = 'original') -> Iterator[np.ndarray]:
  for filename in sorted(glob.glob(image_path(_FILE_PATTERN, subdir))):
    yield (
      path.basename(filename),
      cv2.imread(filename, flags=cv2.IMREAD_UNCHANGED))


def grids(subdir: str = 'original') -> Iterator[Tuple[str, grid.Grid]]:
  for name, image in images(subdir):
    yield name, grid.Grid(image)


def diff_property(prop: str) -> None:
  for name, grid in grids():
    os.makedirs(path.join(data.project_path('data/grid'), prop), exist_ok=True)
    Image.fromarray(getattr(grid, prop)).save(
        image_path(name, prop))
    # TODO: Diff.


with description('grid', 'end2end') as self:
  with it('grayscale'):
    with benchmark(2250):
      diff_property('grayscale')

  with it('threshold'):
    with benchmark(2000):
      diff_property('threshold')

  with it('with_components'):
    with benchmark(7900):
      diff_property('with_components')

  with it('with_largest_component'):
    with benchmark(8000):
      diff_property('with_largest_component')

  with it('with_lines'):
    with benchmark(3500, stddev=.25):  # 3800
      diff_property('with_lines')

  with it('calculates dimensions'):
    with benchmark(2000, stddev=.25):  # 2500
      # These don't work with current method.
      todo = {
        'askew.png',  # Strange angles.
        'nonogram.png',  # Number bank.
        'pentopia.png',  # Shape bank.
        'skyscraper.png',  # Numbers on perimeter.
        'strimko.png',  # Round shapes.
        'thermo.png',  # Needs thresholding.
        'wordsearch.png',  # Fractional cell sizes.
        'wordsearch_with_bank.png',  # Strange shape with word bank.
      }
      focus = {}
      expected = {
        'cages.png': grid.Dimensions(rows=14, columns=14),
        'crossword.png': grid.Dimensions(rows=15, columns=15),
        'fillomino.png': grid.Dimensions(rows=10, columns=10),
        'kakuro.png': grid.Dimensions(rows=12, columns=11),
        'kenken.png': grid.Dimensions(rows=6, columns=6),
        'masyu.png': grid.Dimensions(rows=12, columns=13),
        'multi.png': grid.Dimensions(rows=15, columns=15),
        'nurimaze.png': grid.Dimensions(rows=17, columns=17),
        'slitherlink.png': grid.Dimensions(rows=9, columns=10),
      }
      for name, g in grids():
        if focus and name not in focus:
          continue
        elif name in todo:
          continue
        expect(g.dimensions).to(equal(call(expected.get, name)))

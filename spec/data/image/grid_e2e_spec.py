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

  with it('diffs with_components'):
    with benchmark(7900):
      diff_property('with_components')

  with it('diffs with_largest_component'):
    with benchmark(8000):
      diff_property('with_largest_component')

  with it('diffs with_lines'):
    with benchmark(3500, stddev=.25):
      diff_property('with_lines')

  with it('calculates dimensions'):
    with benchmark(2000, stddev=.25):
      # These don't work with current method.
      todo = {
        'askew.png',  # Strange angles.
        'nonogram.png',  # Number bank.
        'pentopia.png',  # Shape bank.
        'strimko.png',  # Round shapes.
        'wordsearch.png',  # Fractional cell sizes.
        'wordsearch_with_bank.png',  # Strange shape and word bank.
        # Temporarily broken:
        'kakuro.png',  # With numbers extracted borders are too thick.
        'thermo.png',  # Grid optimizations.
      }
      expected = {
        'cages.png': grid.Dimensions(rows=14, columns=14),
        'crossword.png': grid.Dimensions(rows=15, columns=15),
        'castlewall.png': grid.Dimensions(rows=11, columns=12),
        'fillomino.png': grid.Dimensions(rows=10, columns=10),
        'kakuro.png': grid.Dimensions(rows=11, columns=11),
        'kenken.png': grid.Dimensions(rows=6, columns=6),
        'masyu.png': grid.Dimensions(rows=12, columns=13),
        'multi.png': grid.Dimensions(rows=15, columns=15),
        'nurimaze.png': grid.Dimensions(rows=17, columns=17),
        'skyscraper.png': grid.Dimensions(rows=6, columns=6),
        'slitherlink.png': grid.Dimensions(rows=9, columns=10),
        'thermo.png': grid.Dimensions(rows=10, columns=9),  # Has title row.
      }
      for name, g in grids():
        if name in todo:
          continue
        expect(g.dimensions).to(equal(call(expected.get, name)))

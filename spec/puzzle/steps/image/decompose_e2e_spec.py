import collections
import glob
from os import path

import cv2

from data import data, warehouse
from data.image import image
from puzzle.constraints.image import decompose_constraints, \
  prepare_image_constraints
from puzzle.puzzlepedia import prod_config
from puzzle.steps.image import decompose, prepare_image
from spec.mamba import *

_FILE_PATTERN = '*.png'
_EXPECTED_SYMBOLS = {
  'arrow.png': collections.Counter({'A': 1, 'B': 1}),
  'askew.png': collections.Counter(),
  'cages.png': collections.Counter(),
  # TODO: This entry is missing a 3.
  'castlewall.png': collections.Counter({
    '1': 2, '2': 5, '3': 5, '5': 1,
    'DOWN_ARROW': 5,
    'RIGHT_ARROW': 4,
    'LEFT_ARROW': 3,
    'UP_ARROW': 2,
  }),
  # TODO: This entry is incomplete.
  'crossword.png': collections.Counter(),
  'fillomino.png': collections.Counter({
    '1': 10, '2': 5, '3': 9, '4': 12, '6': 6
  }),
  # TODO: This entry is incomplete.
  'kakuro.png': collections.Counter({'1': 27, 'BACKSLASH': 29}),
  'kenken.png': collections.Counter({
    '0': 3,
    '1': 2,
    '2': 4,
    '3': 3,
    '4': 1,
    '7': 1,
    '6': 4,
    '8': 1,
    '9': 1,
    'ADD': 4,
    'MULTIPLY': 7,
    'DIVIDE': 3,
  }),
  'masyu.png': collections.Counter({'EMPTY_CIRCLE': 25, 'FULL_CIRCLE': 15}),
  'multi.png': collections.Counter(),
  'nonogram.png': collections.Counter({
    '0': 5,
    '1': 118,
    '2': 53,
    '3': 27,
    '4': 11,
    '5': 6,
    '6': 10,
    '7': 8,
    '8': 1,
    '9': 3,
  }),
  'nurimaze.png': collections.Counter({'FULL_CIRCLE': 4}),
  # TODO: This entry is incomplete.
  'pentopia.png': collections.Counter({'UP_ARROW': 6, 'DOWN_ARROW': 3, 'T': 1}),
  'skyscraper.png': collections.Counter(),
  'slitherlink.png': collections.Counter(),
  'spiral.png': collections.Counter(),
  'strimko.png': collections.Counter({
    '2': 1,
    '3': 1,
    '4': 1,
    'FULL_CIRCLE': 13,
  }),
  'thermo.png': collections.Counter({
    'T': 1, 'h': 1, 'e': 1, 'r': 1, 'm': 1,
    'S': 1, 'u': 2, 'd': 1, 'o': 2, 'k': 1,
    '1': 2,
    '2': 2,
    '3': 2,
    '4': 1,
    '5': 2,
    '6': 2,
    '7': 4,
    '8': 1,
    '9': 2,
  }),
  'wordsearch.png': collections.Counter(),
  'wordsearch_with_bank.png': collections.Counter(),
}
_FOCUS = {
}


def image_path(pattern: str) -> str:
  return path.join(data.project_path('data/grid/original'), pattern)


def images() -> Iterable[Tuple[str, image.Image]]:
  for filename in sorted(glob.glob(image_path(_FILE_PATTERN))):
    yield (
      path.basename(filename),
      image.Image(cv2.imread(filename, flags=cv2.IMREAD_UNCHANGED)))


def prepare_images() -> Iterable[Tuple[str, prepare_image.PrepareImage]]:
  for n, img in images():
    if _FOCUS and n not in _FOCUS:
      continue
    yield n, prepare_image.PrepareImage(
        prepare_image_constraints.PrepareImageConstraints(), img)


with description('decompose', 'end2end') as self:
  with before.all:
    warehouse.save()
    prod_config.init()
    self.prepare_images = list(prepare_images())

  with before.each:
    self.constraints = decompose_constraints.DecomposeConstraints()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('constructs without error'):
    for name, prepare in self.prepare_images:
      expect(
          calling(decompose.Decompose, self.constraints, prepare)
      ).not_to(raise_error)

  with it('finds expected symbols'):
    with benchmark(1300):
      with gather_exceptions() as collector:
        for name, prepare in self.prepare_images:
          d = decompose.Decompose(self.constraints, prepare)
          found = []
          for c in d.get_components():
            symbol = c.labels.get('symbol')
            if symbol:
              found.append(symbol)
          with collector():
            expect(_EXPECTED_SYMBOLS).to(
                have_key(name, collections.Counter(found)))

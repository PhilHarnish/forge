import numpy as np

from data.image import utils
from spec.mamba import *

with description('utils'):
  with description('antialias'):
    with it('expands input image'):
      given = np.array([
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0],
      ], dtype=np.uint8)
      actual = utils.antialias(given)
      expect(actual.min()).to(be_above(0))

  with description('crop'):
    with it('removes 0 pixels'):
      given = np.array([
        [0, 0, 0],
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
      ])
      expected = np.array([
        [1],
        [1],
      ])
      expect(utils.crop(given, 0).tolist()).to(equal(expected.tolist()))

    with it('removes rgb pixels'):
      b = [0, 0, 0]
      w = [255, 255, 255]
      given = np.array([
        [w, w, w],
        [w, b, w],
        [w, w, w],
      ])
      expected = np.array([
        [b],
      ])
      actual = utils.crop(given, w)
      expect(calling(np.array_equal, expected, actual)).to(equal(True))

  with description('kernel_circle'):
    with it('returns a point for size 1'):
      expect(utils.kernel_circle(1).tolist()).to(equal([[1]]))

    with it('returns a cross at small sizes'):
      expect(utils.kernel_circle(3).tolist()).to(
          equal(utils.kernel_cross(3).tolist()))

    with it('returns a circle shape at larger sizes'):
      expect(utils.kernel_circle(5).tolist()).to(equal([
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
      ]))

  with description('kernel_cross'):
    with it('returns a point for size 1'):
      expect(utils.kernel_cross(1).tolist()).to(equal([[1]]))

    with it('returns a cross shape at larger sizes'):
      expect(utils.kernel_cross(5).tolist()).to(equal([
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
      ]))
  with description('morph_open'):
    with it('erases points'):
      expect(utils.morph_open(np.array([
        [1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0],
      ], dtype=np.uint8)).max()).to(equal(0))

    with it('preserves a circle'):
      expect(utils.morph_open(utils.kernel_circle(5)).tolist()).to(
          equal(utils.kernel_circle(5).tolist()))

  with description('outline_and_fill'):
    with it('expands a point'):
      src = np.zeros((7, 7), dtype=np.uint8)
      src[3][3] = 255
      outline, fill = utils.outline_and_fill(src, 2, 1)
      expect(outline.tolist()).to(equal([
        [0, 0, 0, 255, 0, 0, 0],
        [0, 0, 255, 0, 255, 0, 0],
        [0, 255, 0, 0, 0, 255, 0],
        [255, 0, 0, 0, 0, 0, 255],
        [0, 255, 0, 0, 0, 255, 0],
        [0, 0, 255, 0, 255, 0, 0],
        [0, 0, 0, 255, 0, 0, 0]
      ]))
      expect(fill.tolist()).to(equal([
        [0, 0, 0, 255, 0, 0, 0],
        [0, 0, 255, 255, 255, 0, 0],
        [0, 255, 255, 255, 255, 255, 0],
        [255, 255, 255, 255, 255, 255, 255],
        [0, 255, 255, 255, 255, 255, 0],
        [0, 0, 255, 255, 255, 0, 0],
        [0, 0, 0, 255, 0, 0, 0]
      ]))

  with description('preserve_stroke'):
    with it('removes noise'):
      given = np.array([
        [0, 0, 0],
        [0, 255, 0],
        [0, 0, 0],
      ], dtype=np.uint8)
      actual = utils.preserve_stroke(given, 255, 1)
      expect(actual.max()).to(equal(0))

    with it('preserves lines'):
      given = np.array([
        [0, 0, 0, 0, 255, 0, 0, 0, 0],
      ] * 9, dtype=np.uint8)
      actual = utils.preserve_stroke(given, 255, 0.9)
      expect(actual.max()).to(equal(255))

    with it('erases skinny lines'):
      given = np.array([
        [0, 0, 0, 0, 255, 0, 0, 0, 0],
      ] * 9, dtype=np.uint8)
      actual = utils.preserve_stroke(given, 255, 2)
      expect(actual.max()).to(equal(0))

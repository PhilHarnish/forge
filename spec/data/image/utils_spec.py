import numpy as np

from data.image import utils
from spec.mamba import *

with description('utils'):
  with description('crop'):
    with it('removes 0 pixels'):
      given = np.array([
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0],
      ])
      expected = np.array([
        [1],
      ])
      expect(utils.crop(given, 0)).to(equal(expected))

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
        [0, 0, 1, 0, 0]
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
        [0, 0, 1, 0, 0]
      ]))

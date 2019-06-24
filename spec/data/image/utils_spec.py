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

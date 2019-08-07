import numpy as np

from data.image import coloring
from spec.mamba import *

with description('coloring'):
  with description('colors') as self:
    with before.each:
      self.tolist = lambda x: np.array(list(x)).tolist()

    with it('returns 0 colors if requested'):
      expect(coloring.colors(0)).to(be_empty)

    with it('returns only black and white if requested'):
      expect(self.tolist(coloring.colors(2, with_black_and_white=True))).to(
          equal(np.array([
            [0, 0, 0],
            [255, 255, 255]
          ]).tolist()))

    with it('returns unique colors'):
      expect(self.tolist(coloring.colors(200))).to(be_unique)

  with description('color_band'):
    with it('returns nothing if not matched'):
      src = np.zeros((3, 3), dtype=np.uint8)
      expect(coloring.color_band(src, 1).tolist()).to(equal([
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
      ]))

    with it('returns matches'):
      src = np.zeros((3, 3), dtype=np.uint8)
      expect(coloring.color_band(src, 0).tolist()).to(equal([
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
      ]))

    with it('matches range'):
      src = np.arange(0, 10, dtype=np.uint8)
      expect(coloring.color_band(src, 2, 5).tolist()).to(equal(
          [0, 0, 255, 255, 255, 255, 0, 0, 0, 0]))

  with description('enhance'):
    with it('does not modify zeros'):
      given = np.zeros((3, 3), dtype=np.uint8)
      expect(coloring.enhance(given).tolist()).to(equal(given.tolist()))

    with it('does not modify black and white'):
      given = np.zeros((3, 3), dtype=np.uint8)
      given[1][1] = coloring.MAX
      expect(coloring.enhance(given).tolist()).to(equal(given.tolist()))

    with it('scales up to reach MAX'):
      given = np.array([
        [0] * 10,
        [10] * 10,
        [200] * 10,
      ], dtype=np.uint8)
      expect(coloring.enhance(given).max()).to(equal(coloring.MAX))

  with description('normalize'):
    with it('handles monochrome'):
      expect(coloring.normalize(np.zeros((4, 5), dtype=np.uint8)).shape).to(
          equal((4, 5, 3)))

    with it('handles RGB'):
      expect(coloring.normalize(np.zeros((4, 5, 3), dtype=np.uint8)).shape).to(
          equal((4, 5, 3)))

    with it('handles RGBA'):
      expect(coloring.normalize(np.zeros((4, 5, 4), dtype=np.uint8)).shape).to(
          equal((4, 5, 3)))

  with description('top_n_color_clusters'):
    with it('generates empty output for empty input'):
      expect(coloring.top_n_color_clusters(np.array([]), 10)).to(be_empty)

    with it('yields significant values'):
      expect(list(coloring.top_n_color_clusters(np.array([
        1000, 0, 500, 0, 1000,
      ]), 3, threshold=1))).to(equal([[0], [2], [4]]))

    with it('large values near each other are clustered'):
      expect(list(coloring.top_n_color_clusters(np.array([
        1000, 0, 700, 500, 600, 0, 1000,
      ]), 6, threshold=1))).to(equal([[0], [2, 3, 4], [6]]))

    with it('clusters are split if there are gaps'):
      expect(list(coloring.top_n_color_clusters(np.array([
        1000, 0, 700, 0, 600, 0, 1000,
      ]), 6, threshold=1))).to(equal([[0], [2], [4], [6]]))

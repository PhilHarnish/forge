import math

import numpy as np

from spec.mamba import *
from util.geometry import np2d

(
  TL, T, TR,
  L, M, R,
  BL, B, BR,
) = np.array([
  (0, 2), (1, 2), (2, 2),
  (0, 1), (1, 1), (2, 1),
  (0, 0), (1, 0), (2, 0),
])


with description('np2d'):
  with description('iter_segments'):
    with it('iterates list of coordinates'):
      segments = np.array(list(np2d.iter_segments(np.array([
        TL, TR, BR, BL,
      ]))))
      expect(segments.tolist()).to(equal(np.array([
        (TL, TR), (TR, BR), (BR, BL), (BL, TL),
      ]).tolist()))

  with description('orientation'):
    with it('identifies colinear'):
      expect(np2d.orientation(L, M, R)).to(equal(0))
      expect(np2d.orientation(BL, M, TR)).to(equal(0))
      expect(np2d.orientation(BR, M, TL)).to(equal(0))

    with it('distinguishes different directions'):
      expect(np2d.orientation(L, R, B)).not_to(equal(
          np2d.orientation(L, B, R)))

  with description('overlap'):
    with it('returns 0 for non-overlapping lines'):
      expect(np2d.overlap((BL, B), (M, R))).to(equal(0))

    with it('returns 0 for steep inclines'):
      expect(np2d.overlap((BL, BR), (TL, BR))).to(equal(0))

    with it('returns overlap'):
      expect(np2d.overlap((BL, BR), (M, R))).to(equal(1))

    with it('allows steep inclines if specified'):
      expect(np2d.overlap((BL, BR), (M, BR), threshold=math.pi)).to(equal(1))

  with description('point_to_point_distance'):
    with it('returns 0 for coincident points'):
      expect(np2d.point_to_point_distance(M, M)).to(equal(0.0))

    with it('returns distance between separated points'):
      expect(np2d.point_to_point_distance(L, R)).to(equal(2.0))

  with description('point_to_segment_distance'):
    with it('returns 0 for intersections'):
      expect(np2d.point_to_segment_distance(M, (L, R))).to(equal(0.0))

    with it('returns distance in the generial case'):
      expect(np2d.point_to_segment_distance(T, (L, R))).to(equal(1.0))

    with it('returns distance to left edge when off left side'):
      expect(np2d.point_to_segment_distance(L, (M, R))).to(equal(1.0))

    with it('returns distance to left edge when off right side'):
      expect(np2d.point_to_segment_distance(R, (M, L))).to(equal(1.0))

  with description('slope'):
    with it('returns 0 for horizontal'):
      expect(np2d.slope((L, R))).to(equal(0))

    with it('returns pi/2 for vertical'):
      expect(np2d.slope((T, B))).to(equal(math.pi / 2))

  with description('segments_intersect'):
    with it('returns false for parallel lines'):
      expect(np2d.segments_intersect((TL, TR), (BL, BR))).to(be_false)

    with it('returns true for intersecting lines'):
      expect(np2d.segments_intersect((T, B), (L, R))).to(be_true)

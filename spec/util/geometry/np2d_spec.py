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


_EAST_MIRROR = (
  np.array([[1315,  786], [1422,  788]]),
  np.array([[1422,  783], [1315,  784]]),
)
_SSE = (
  np.array([[770, 1360], [779, 1467]]),
  np.array([[782, 1468], [774, 1360]]),
)
_1U_APART = (
  np.array([[105, 151], [ 82, 137]]),
  np.array([[ 79, 167], [103, 181]]),
)
# Tuples of (line1, line2).
_OVERLAP_REGRESSION_TESTS = [
  (
    np.array([[86, 194], [88, 192]]),
    np.array([[89, 190], [84, 192]]),
  ),
  (
    np.array([[ 88, 192], [ 93, 190]]),
    np.array([[ 91, 188], [ 89, 190]]),
  ),
  (
    np.array([[ 93, 190], [ 95, 188]]),
    np.array([[ 96, 186], [ 91, 188]]),
  ),
  (
    np.array([[ 95, 188], [100, 186]]),
    np.array([[ 98, 184], [ 96, 186]]),
  ),
]


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
    expect(np2d.overlap((BL, BR), (M, R))).to(equal(1 / ((2 + 1) / 2)))

  with it('rejects gaps greater than specified'):
    segment_length = np2d.point_to_point_distance(*_1U_APART[0])
    expect(np2d.overlap(*_1U_APART, gap_threshold=segment_length * 0.9)).to(
        equal(0))

  with it('accepts gaps given sufficient threshold'):
    segment_length = np2d.point_to_point_distance(*_1U_APART[0])
    expect(np2d.overlap(*_1U_APART, gap_threshold=segment_length * 1.1)).to(
        be_above(.5))

  with it('does not regress on earlier segments'):
    for s1, s2 in _OVERLAP_REGRESSION_TESTS:
      expect(calling(np2d.overlap, s1, s2)).to(be_above(.5))

with description('point_intersect_box'):
  with it('accepts a point inside the box'):
    expect(np2d.point_intersect_box(M, 0, 3, 3)).to(be_true)

  with it('accepts line L -> R from outside'):
    expect(np2d.point_intersect_box((-1, 1), 0, 3, 3)).to(be_true)

  with it('accepts line T -> B from outside'):
    expect(np2d.point_intersect_box((1, -1), math.pi / 2, 3, 3)).to(be_true)

  with it('accepts line TL -> BR from outside'):
    expect(np2d.point_intersect_box((-1, -1), math.pi / 4, 3, 3)).to(be_true)

  with it('rejects line tangential to box from outside'):
    expect(np2d.point_intersect_box((-1, -1), 3 * math.pi / 4, 3, 3)).to(
        be_false)

  with it('accepts regression tests'):
    # These are from real images.
    scenarios = [
      ((301.0, 1825.5), math.pi / 2, 602, 602),
      ((1825.5, 301.0), math.pi, 602, 602),
      ((1825.5, 301.0), 0, 602, 602),
      ((1825.5, 1825.5), math.pi / 4, 602, 602),
      ((309.0, 532.0), 4.1889050520600115, 988, 850),
    ]
    for args in scenarios:
      expect(calling(np2d.point_intersect_box, *args)).to(equal(True))

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

with description('polar_line_intersect'):
  with it('finds intersections'):
    horizontal = (1, 0)
    vertical = (1, math.pi / 2)
    x, y = np2d.polar_line_intersect(horizontal, vertical)
    expect(x).to(be_between(.99, 1.01))
    expect(y).to(be_between(.99, 1.01))

with description('slope'):
  with it('returns 0 for horizontal'):
    expect(np2d.slope((L, R))).to(equal(0))

  with it('returns pi/2 for vertical'):
    expect(np2d.slope((T, B))).to(equal(math.pi / 2))

with description('slopes'):
  with it('returns slopes for horizontal segments'):
    expect(np.degrees(np2d.slopes((L, M), (M, R))).tolist()).to(equal(
        [0, 0, 0]))

  with it('returns slopes for right angle segments'):
    expect(np.degrees(np2d.slopes((T, M), (M, R))).tolist()).to(equal(
        [90, 0, 90]))

  with it('returns small delta segments nearly pointing east'):
    _, _, delta = np.degrees(np2d.slopes(*_EAST_MIRROR)).tolist()
    expect(delta).to(be_between(0, 2))

  with it('returns small delta for segments pointing SSE'):
    _, _, delta = np.degrees(np2d.slopes(*_SSE)).tolist()
    expect(delta).to(be_between(0, 2))

with description('segments_intersect'):
  with it('returns false for parallel lines'):
    expect(np2d.segments_intersect((TL, TR), (BL, BR))).to(be_false)

  with it('returns true for intersecting lines'):
    expect(np2d.segments_intersect((T, B), (L, R))).to(be_true)

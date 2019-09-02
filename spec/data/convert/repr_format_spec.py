import numpy as np

from spec.mamba import *

with description('as_args'):
  with it('returns nothing for empty input'):
    expect(repr_format.as_args()).to(equal(''))

  with it('returns comma separated variable args'):
    expect(repr_format.as_args(1, True, 'string', {'set'})).to(
        equal("1, True, 'string', {'set'}"))

  with it('returns comma separated kwargs'):
    expect(repr_format.as_args(a=1, b='string', c={'set'})).to(
        equal("a=1, b='string', c={'set'}"))

  with it('sorts kwargs'):
    expect(repr_format.as_args(
        a=1, z=2, b=3, y=4, c=5, x=6,
    )).to(equal('a=1, b=3, c=5, x=6, y=4, z=2'))


with description('repr_ndarray'):
  with it('handles zeros'):
    expect(repr_format.repr_ndarray(np.zeros((1, 2)))).to(equal(
        'np.zeros((1, 2))'))

  with it('handles ones'):
    expect(repr_format.repr_ndarray(np.ones((3, 4)))).to(equal(
        'np.ones((3, 4))'))

  with it('handles modified ones'):
    v = np.ones((3, 4))
    v[0][0] = 0
    expect(repr_format.repr_ndarray(v)).to(equal('np.array(shape=(3, 4))'))

  with it('handles custom dtype'):
    expect(repr_format.repr_ndarray(np.ones((3, 4), dtype=np.uint8))).to(equal(
        'np.ones((3, 4), dtype=np.uint8)'))


with description('repr_value'):
  with it('reprs primitives'):
    for v in (None, True, 1, 'string'):
      expect(calling(repr_format.repr_value, v)).to(equal(repr(v)))

  with it('reprs ndarrays'):
    v = np.array([1, 2])
    expect(repr_format.repr_value(v)).not_to(equal(repr(v)))

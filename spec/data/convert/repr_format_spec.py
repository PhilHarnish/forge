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

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

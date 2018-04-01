from data import fixed_dict
from spec.mamba import *


with description('FixedDict'):
  with it('raises on 0'):
    expect(calling(fixed_dict.FixedDict, 0)).to(raise_error(ValueError))

  with it('accepts 1+ values'):
    for x in range(1, 5):
      expect(calling(fixed_dict.FixedDict, x)).not_to(raise_error)

  with it('never exceeds specified length'):
    for x in range(1, 5):
      d = fixed_dict.FixedDict(x)
      for c in 'abcdefg':
        d[c] = True
        expect(d).to(have_len(be_below_or_equal(x)))

  with it('is not affected by duplicates'):
    d = fixed_dict.FixedDict(3)
    d['x'] = 0
    d['y'] = 0
    for i, c in enumerate('aaaaaa'):
      d[c] = i
      expect(d).to(equal({'a': i, 'x': 0, 'y': 0}))
    d['b'] = 0
    expect(d).to(equal({'a': 5, 'b': 0, 'y': 0}))

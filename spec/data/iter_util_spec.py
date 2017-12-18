from data import iter_util
from spec.mamba import *


with description('common'):
  with it('returns nothing for empty input'):
    expect(iter_util.common([])).to(equal([]))

  with it('returns all items for single object'):
    expect(iter_util.common([{'a': 1, 'b': .5}])).to(equal([
      ('a', [1]),
      ('b', [.5]),
    ]))

  with it('returns common items for multiple'):
    expect(iter_util.common([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ])).to(equal([
      ('b', [.5, .25]),
    ]))

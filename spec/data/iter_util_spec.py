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

  with it('optionally focuses specified items'):
    expect(iter_util.common([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ], whitelist={'b'})).to(equal([
      ('b', [.5, .25]),
    ]))

  with it('optionally skips specified items'):
    expect(iter_util.common([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ], blacklist={'b'})).to(equal([]))

  with it('optionally skips and focuses specified items'):
    expect(iter_util.common([
        {'a': 1, 'b': 1, 'c': 1},
        {'_': 2, 'b': 2, 'c': 2},
    ], whitelist={'b'}, blacklist={'c'})).to(equal([
      ('b', [1, 2]),
    ]))


with description('both'):
  with it('returns nothing for empty input'):
    expect(iter_util.both([])).to(equal([]))

  with it('returns all items for single object'):
    expect(list(sorted(iter_util.both([{'a': 1, 'b': .5}])))).to(equal([
      ('a', [1]),
      ('b', [.5]),
    ]))

  with it('returns either items for multiple'):
    expect(list(sorted(iter_util.both([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ])))).to(equal([
      ('a', [1]),
      ('b', [0.5, 0.25]),
      ('c', [0.15]),
    ]))

  with it('optionally focuses specified items'):
    expect(iter_util.both([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ], whitelist={'b'})).to(equal([
      ('b', [.5, .25]),
    ]))

  with it('optionally skips specified items'):
    expect(list(sorted(iter_util.both([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ], blacklist={'b'})))).to(equal([
      ('a', [1]),
      ('c', [0.15]),
    ]))

  with it('optionally skips and focuses specified items'):
    expect(list(sorted(iter_util.both([
        {'a': 1, 'b': 1, 'c': 1},
        {'_': 2, 'b': 2, 'c': 2},
    ], whitelist=set('abc'), blacklist={'c'})))).to(equal([
      ('a', [1]),
      ('b', [1, 2]),
    ]))

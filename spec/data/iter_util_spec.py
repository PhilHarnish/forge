from data import iter_util
from spec.mamba import *


with description('common'):
  with it('returns nothing for empty input'):
    expect(iter_util.map_common([])).to(equal([]))

  with it('returns all items for single object'):
    expect(iter_util.map_common([{'a': 1, 'b': .5}])).to(equal([
      ('a', [1]),
      ('b', [.5]),
    ]))

  with it('returns common items for multiple'):
    expect(iter_util.map_common([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ])).to(equal([
      ('b', [.5, .25]),
    ]))

  with it('optionally focuses specified items'):
    expect(iter_util.map_common([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ], whitelist={'b'})).to(equal([
      ('b', [.5, .25]),
    ]))

  with it('optionally skips specified items'):
    expect(iter_util.map_common([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ], blacklist={'b'})).to(equal([]))

  with it('optionally skips and focuses specified items'):
    expect(iter_util.map_common([
        {'a': 1, 'b': 1, 'c': 1},
        {'_': 2, 'b': 2, 'c': 2},
    ], whitelist={'b'}, blacklist={'c'})).to(equal([
      ('b', [1, 2]),
    ]))


with description('both'):
  with it('returns nothing for empty input'):
    expect(iter_util.map_both([])).to(equal([]))

  with it('returns nothing for empty input + whitelist'):
    expect(iter_util.map_both([{'key': 'value'}], whitelist={' '})).to(equal([]))

  with it('returns all items for single object'):
    expect(list(sorted(iter_util.map_both([{'a': 1, 'b': .5}])))).to(equal([
      ('a', [1]),
      ('b', [.5]),
    ]))

  with it('returns either items for multiple'):
    expect(list(sorted(iter_util.map_both([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ])))).to(equal([
      ('a', [1]),
      ('b', [0.5, 0.25]),
      ('c', [0.15]),
    ]))

  with it('optionally focuses specified items'):
    expect(iter_util.map_both([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ], whitelist={'b'})).to(equal([
      ('b', [.5, .25]),
    ]))

  with it('optionally skips specified items'):
    expect(list(sorted(iter_util.map_both([
        {'a': 1, 'b': .5},
        {'b': .25, 'c': .15},
    ], blacklist={'b'})))).to(equal([
      ('a', [1]),
      ('c', [0.15]),
    ]))

  with it('optionally skips and focuses specified items'):
    expect(list(sorted(iter_util.map_both([
        {'a': 1, 'b': 1, 'c': 1},
        {'_': 2, 'b': 2, 'c': 2},
    ], whitelist=set('abc'), blacklist={'c'})))).to(equal([
      ('a', [1]),
      ('b', [1, 2]),
    ]))


with description('none'):
  with it('returns nothing for empty input'):
    expect(iter_util.map_none([])).to(equal([]))

  with it('returns nothing for simple input'):
    expect(iter_util.map_none([{}, {'key': 'value'}])).to(equal([]))


with description('reduce binary'):
  with before.each:
    self.reducer = mock.Mock('reducer', side_effect=lambda a, b: a + b)

  with it('returns input for 1 value'):
    expect(iter_util.reduce_binary(self.reducer, [1])).to(equal(1))

  with it('returns sum for 2 values'):
    expect(iter_util.reduce_binary(self.reducer, [1, 2])).to(equal(3))

  with it('returns sum for many values'):
    expect(iter_util.reduce_binary(self.reducer, range(16))).to(
        equal(sum(range(16))))

  with it('calls reducer a minimum number of times'):
    iter_util.reduce_binary(self.reducer, range(32))
    expect(self.reducer).to(have_been_called_times(31))

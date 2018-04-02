from data import iter_util
from spec.mamba import *


with description('map_both'):
  with it('returns nothing for empty input'):
    expect(iter_util.map_both([])).to(equal([]))

  with it('returns nothing for whitelist miss'):
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


with description('map_common'):
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


with description('map_none'):
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


with description('ensure_prefix') as self:
  with before.each:
    self.subject = lambda *args: list(iter_util.ensure_prefix(args[0], args[1]))

  with it('returns nothing for empty input'):
    expect(self.subject([], [])).to(equal([]))

  with it('returns from first if only first is provided'):
    expect(self.subject(['a', 'b', 'c'], [])).to(equal(['a', 'b', 'c']))

  with it('returns from first if only second is provided'):
    expect(self.subject([], ['a c', 'b b', 'c a'])).to(equal(['a', 'b', 'c']))

  with it('ignores second if prefixes are already ensured'):
    expect(self.subject(['a', 'b', 'c'], ['a c', 'b b', 'c a'])).to(
        equal(['a', 'b', 'c']))

  with it('invents prefixes if required'):
    expect(self.subject(['a', 'c'], ['a c', 'b b', 'c a'])).to(
        equal(['a', 'b', 'c']))

  with it('does not invents prefixes if not required'):
    expect(self.subject(['a', 'c'], ['a c', 'c a'])).to(equal(['a', 'c']))

  with it('does emit duplicates if reference is redundant'):
    expect(self.subject([], ['a a', 'a b', 'a c'])).to(equal(['a']))


with description('iter_alphabetical_prefixes') as self:
  with before.each:
    self.subject = lambda x: list(iter_util.iter_alphabetical_prefixes(x))

  with it('returns nothing for empty input'):
    expect(self.subject([])).to(equal([]))

  with it('returns given results for one iterable'):
    expect(self.subject([['a']])).to(equal([('a', None)]))

  with it('returns grouped results for one iterable'):
    expect(self.subject([['a', 'b']])).to(equal([('a', None), ('b', None)]))

  with it('groups similar results for multiple iterables'):
    expect(self.subject([['a', 'b'], ['a a', 'a b']])).to(
        equal([('a', [('a a', None), ('a b', None)]), ('b', [])]))

  with it('groups many results for multiple iterables'):
    expect(self.subject([
      ['a',     'b',                      'c'],
      ['a a',   'b a', 'b b',             'c a'],
      ['a a a', 'b a a', 'b b a', 'b b b'],
    ])).to(equal([
      ('a', [('a a', [('a a a', None)])]),
      ('b', [
        ('b a', [('b a a', None)]),
        ('b b', [('b b a', None), ('b b b', None)]),
      ]),
      ('c', [('c a', [])]),
    ]))

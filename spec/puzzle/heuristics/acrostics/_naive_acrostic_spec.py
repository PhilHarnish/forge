import mock
from expects import *

from puzzle.heuristics.acrostics import _naive_acrostic
from spec.data.fixtures import tries
from src.data import word_frequencies

BA_PREFIX_TRIE = word_frequencies.load(
    zip(('bad', 'bag', 'ban', 'bar', 'bat'), [1]*5))


with _description('acrostic'):
  with it('uses a mock trie'):
    a = _naive_acrostic.Acrostic(['a'], tries.letters())
    expect(len(a._trie)).to(be_below(100))

  with it('yields simple solutions'):
    a = _naive_acrostic.Acrostic(['a'], tries.letters())
    expect(list(a)).to(contain('a'))

  with it('is observable'):
    a = _naive_acrostic.Acrostic(['a'], tries.letters())
    subs = mock.Mock()
    a.subscribe(subs)
    expect(subs.on_next.call_args).to(equal(mock.call('a')))

  with it('yields multi-character solutions'):
    a = _naive_acrostic.Acrostic(list('bag'), BA_PREFIX_TRIE)
    expect(list(a)).to(contain('bag'))

  with it('yields unique solutions'):
    a = _naive_acrostic.Acrostic(list('ba') + ['ggg'], BA_PREFIX_TRIE)
    expect(list(a)).to(have_len(1))

  with it('yields multiple multi-character solutions'):
    a = _naive_acrostic.Acrostic(list('ba') + ['dgnrt'], BA_PREFIX_TRIE)
    expect(list(a)).to(contain('bad', 'bag', 'ban', 'bar', 'bat'))

  with context('benchmark'):
    with it('finds simple solutions quickly'):
      a = _naive_acrostic.Acrostic(['a'], tries.letters())
      expect(list(a)).to(contain('a'))
      expect(a.cost()).to(equal(1))

    with it('ignores duplicate characters'):
      a = _naive_acrostic.Acrostic([
        'bbbbbb',
        'a',
        'g',
      ], BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bag'))
      expect(a.cost()).to(equal(1))

    with it('ignores invalid words'):
      a = _naive_acrostic.Acrostic([
        'b',
        'a',
        'abcefg',
      ], BA_PREFIX_TRIE)
      expect(list(a)).not_to(contain('baa', 'bab', 'bac', 'bae', 'baf'))
      expect(list(a)).to(contain('bag'))
      expect(a.cost()).to(be_above(1))
      expect(a.cost()).to(be_below(10))

    with it('skips invalid prefixes'):
      a = _naive_acrostic.Acrostic([
        'b',
        'abcdefghijklmnopqrstuvwxyz',
        'g',
      ], BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bag'))
      expect(a.cost()).to(be_below(10))

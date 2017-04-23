import mock
from expects import *

from src.data import word_frequencies
from src.puzzle.heuristics import _acrostic_graph
from spec.data.fixtures import tries

BA_PREFIX_TRIE = word_frequencies.load(
    zip(('bad', 'bag', 'ban', 'bar', 'bat'), [1]*5))


with description('_AcrosticGraph'):
  with it('yields multi-character solutions'):
    a = _acrostic_graph._AcrosticGraph(list('bag'), BA_PREFIX_TRIE)
    expect(list(a)).to(contain('bag'))

  with it('yields unique solutions'):
    a = _acrostic_graph._AcrosticGraph(list('ba') + ['ggg'], BA_PREFIX_TRIE)
    expect(list(a)).to(have_len(1))

  with it('yields multiple multi-character solutions'):
    a = _acrostic_graph._AcrosticGraph(list('ba') + ['dgnrt'], BA_PREFIX_TRIE)
    expect(list(a)).to(contain('bad', 'bag', 'ban', 'bar', 'bat'))

  with context('benchmark'):
    with it('finds simple solutions quickly'):
      a = _acrostic_graph._AcrosticGraph(['a'], tries.letters())
      expect(list(a)).to(contain('a'))
      expect(a.cost).to(equal(1))

    with it('ignores duplicate characters'):
      a = _acrostic_graph._AcrosticGraph([
        'bbbbbb',
        'a',
        'g',
      ], BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bag'))
      expect(a.cost).to(equal(1))

    with it('ignores invalid words'):
      a = _acrostic_graph._AcrosticGraph([
        'b',
        'a',
        'abcefg',
      ], BA_PREFIX_TRIE)
      expect(list(a)).not_to(contain('baa', 'bab', 'bac', 'bae', 'baf'))
      expect(list(a)).to(contain('bag'))
      expect(a.cost).to(be_above(1))
      expect(a.cost).to(be_below(10))

    with it('skips invalid prefixes'):
      a = _acrostic_graph._AcrosticGraph([
        'b',
        'abcdefghijklmnopqrstuvwxyz',
        'g',
      ], BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bag'))
      expect(a.cost).to(be_below(10))

from data import word_frequencies
from puzzle.heuristics import acrostic
from spec.mamba import *

BA_PREFIX_TRIE = word_frequencies.load(
    zip(('bad', 'bag', 'ban', 'bar', 'bat'), [1]*5))

with description('acrostic'):
  with it('uses a mock trie'):
    a = acrostic.Acrostic(list('bag'), BA_PREFIX_TRIE)
    expect(len(a._trie)).to(be_below(100))

  with it('yields multi-character solutions'):
    a = acrostic.Acrostic(list('bag'), BA_PREFIX_TRIE)
    expect(list(a)).to(contain('bag'))

  with it('is observable'):
    a = acrostic.Acrostic(list('bag'), BA_PREFIX_TRIE)
    subs = mock.Mock()
    a.subscribe(subs)
    expect(subs.on_next.call_args).to(equal(mock.call('bag')))

  with it('yields unique solutions'):
    a = acrostic.Acrostic(list('ba') + ['ggg'], BA_PREFIX_TRIE)
    expect(list(a)).to(have_len(1))

  with it('yields multiple multi-character solutions'):
    a = acrostic.Acrostic(list('ba') + ['dgnrt'], BA_PREFIX_TRIE)
    expect(list(a)).to(contain('bad', 'bag', 'ban', 'bar', 'bat'))

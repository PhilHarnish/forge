from puzzle.examples.mitmh.year2019 import bubbly
from spec.mamba import *


with description('bubbly'):
  with description('relate_binary'):
    with it('relates small 1 2'):
      relation, remaining = bubbly.relate_binary('a b(c)')
      expect(bubbly.char_dict(relation)).to(equal(
          {'a': 'a', 'b': 'b', 'c': 'bc'}))
      expect(bubbly.chars(remaining)).to(equal('abc'))

    with it('relates 1 mixed, confusing'):
      relation, remaining = bubbly.relate_binary('a(b(c) d)')
      expect(bubbly.char_dict(relation)).to(equal(
          {'a': 'a', 'b': 'ab', 'c': 'abc', 'd': 'ad'}))
      expect(bubbly.chars(remaining)).to(equal('abcd'))

    with it('relates 1 mixed'):
      relation, remaining = bubbly.relate_binary('a(b(c)(d))')
      expect(bubbly.char_dict(relation)).to(equal(
          {'a': 'a', 'b': 'ab', 'c': 'abc', 'd': 'abd'}))
      expect(bubbly.chars(remaining)).to(equal('abcd'))

    with it('raises for extra closes'):
      expect(calling(bubbly.relate_binary, 'a(b)))')).to(raise_error(IndexError))

    with it('raises for extra opens'):
      expect(calling(bubbly.relate_binary, 'a(b(c')).to(raise_error(IndexError))

  with description('will_win_binary'):
    with it('handles trivial single'):
      relation, remaining = bubbly.relate_binary('s')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('s'))

    with it('handles trivial double'):
      relation, remaining = bubbly.relate_binary('s n')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal(''))

    with it('handles trivial triple'):
      relation, remaining = bubbly.relate_binary('a b c')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('abc'))

    with it('handles example'):
      relation, remaining = bubbly.relate_binary('s n t(i) e(a(h))')
      expect(bubbly.chars(remaining)).to(equal('aehinst'))
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('ens'))

    with it('handles 1'):
      relation, remaining = bubbly.relate_binary('n c(g r(a) h(s(t u(i) v(e(l)))))')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('ei'))

    with it('handles 2'):
      relation, remaining = bubbly.relate_binary('e(g) h(v(p(r))) i(f(s n(u)) t(c(a(l))))')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('chs'))

    with it('handles 3'):
      relation, remaining = bubbly.relate_binary('f(p l(u) h(r e(a(n y(m)) c(v i(g t(s))))))')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('er'))

    with it('handles 4'):
      relation, remaining = bubbly.relate_binary('b(g) a(v s(p(e))) m(r(k c(l))) i(y(n(f) u(t(h))))')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('afrt'))

    with it('handles 5'):
      relation, remaining = bubbly.relate_binary('f(n(z k(p)) l(g(m) s(y i(c v(h))) e(b a(r) d(t(u)))))')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('eip'))

    with it('handles 6'):
      relation, remaining = bubbly.relate_binary('s(w) c(i r(p)) a(d u(x) t(f(g)) b(h l(n) e(y z(v m(k)))))')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('el'))

    with it('handles 7'):
      relation, remaining = bubbly.relate_binary('n(e) p(h(w)) f(q(b(v(i)))) r(g(u(l(z(c))))) t(y(a j(m)) s(d(k(x))))')
      expect(bubbly.chars(bubbly.will_win_binary(relation, remaining))).to(
          equal('nrw'))

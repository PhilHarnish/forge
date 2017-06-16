from puzzle.heuristics import analyze_number
from spec.mamba import *

with description('analyze_number'):
  with before.each:
    def run(fn, n, base):
      for digits, _ in analyze_number._get_digits_in_base(n, base):
        min_digit = min(digits)
        max_digit = max(digits)
        for result in fn(digits, min_digit, max_digit):
          yield result


    def first(fn, n, base):
      return next(run(fn, n, base))[0]


    self.run = lambda fn, n, base=10: call(run, fn, n, base)
    self.first = lambda fn, n, base=10: call(first, fn, n, base)

  with description('_get_digits_in_base'):
    with it('converts base'):
      expect(next(analyze_number._get_digits_in_base(
          0x5072697A776172646564746F61757468, 256
      ))).to(equal(
          ([
            0x50, 0x72, 0x69, 0x7A, 0x77, 0x61, 0x72, 0x64,
            0x65, 0x64, 0x74, 0x6F, 0x61, 0x75, 0x74, 0x68
          ], ['base256'])))

    with it('converts base with gaps'):
      results = analyze_number._get_digits_in_base(
          0x50007269007A77006172006465006474006F610075740068, 256
      )
      next(results)  # Burn first result.
      expect(next(results)).to(equal(
          ([
            0x50, 0x72, 0x69, 0x7A, 0x77, 0x61, 0x72, 0x64,
            0x65, 0x64, 0x74, 0x6F, 0x61, 0x75, 0x74, 0x68
          ], ['base256', 'filtered 0 (+1%3)'])))

  with description('alphabet'):
    with it('rejects invalid input'):
      expect(self.run(analyze_number._alphabet, 101)).to(be_empty)

    with it('accepts input'):
      expect(self.first(analyze_number._alphabet, 312)).to(equal('cab'))

  with description('ascii_nibbles'):
    with it('accepts input'):
      expect(self.first(analyze_number._ascii_nibbles, 0x6f776c, 16)).to(
          equal('owl'))

    with it('accepts delimited input'):
      expect(next(analyze_number._ascii_nibbles([
        0x6, 0xf, 16, 0x7, 0x7, 16, 0x6, 0xc,
      ], 6, 16))[0]).to(equal('owl'))

    with it('ignores unusual input'):
      expect(list(analyze_number._ascii_nibbles([
        16
      ], 16, 16))).to(be_empty)

  with description('base_n'):
    with it('rejects invalid input'):
      expect(self.run(analyze_number._base_n, 100)).to(be_empty)

    with it('accepts hex input (A-F)'):
      expect(self.first(analyze_number._base_n, 0xCAB, 16)).to(equal('cab'))

    with it('accepts higher base values (A-Z)'):
      expect(next(analyze_number._base_n([
        14 + 10, 22 + 10, 11 + 10
      ], 22, 32))[0]).to(equal('owl'))

  with description('braille'):
    with it('rejects decreasing input'):
      expect(self.run(analyze_number._braille, 6543)).to(be_empty)

    with it('accepts increasing input'):
      expect(self.first(analyze_number._braille, 135024560123)).to(equal('owl'))

  with description('hex'):
    with it('understands hexspeak'):
      expect(self.first(analyze_number._hexspeak, 0xDEAD, 16)).to(equal('dead'))

  with description('keyboard intersection'):
    with it('rejects odd digit counts'):
      expect(self.run(analyze_number._keyboard_intersection, 101)).to(be_empty)

    with it('accepts valid input'):
      expect(self.first(analyze_number._keyboard_intersection, 361358)).to(
          equal('cab'))

  with description('lexicographical ordering'):
    with it('rejects input with incorrect length'):
      expect(self.run(analyze_number._lexicographical_ordering, 10101)).to(
          be_empty)

    with it('rejects repeated input'):
      expect(self.run(analyze_number._lexicographical_ordering, 1011)).to(
          be_empty)

    with it('accepts lexicographical ordering'):
      # Ordering: 012, 021, 102, 120, 201, 210.
      # Alphabet:   a,   b,   c,   d,   e,   f.
      expect(self.first(
          analyze_number._lexicographical_ordering, 102012021)).to(equal('cab'))

  with description('morse'):
    with it('rejects invalid sequences'):
      expect(self.run(analyze_number._morse, 22222222)).to(be_empty)

    with it('accepts ambiguous sequences'):
      owls = [
        222012201211,  # 012 = ' .-'
        111021102122,  # 012 = ' -.'
        111201120100,  # 012 = '-. '
      ]
      for owl in owls:
        expect(self.first(analyze_number._morse, owl)).to(equal('owl'))

  with description('phone numbers'):
    with it('rejects invalid numbers'):
      samples = [
        123,  # Too short.
        180012345678,  # Too long.
        1234560,  # Contains a zero.
      ]
      for sample in samples:
        expect(self.run(analyze_number._phone_number, sample)).to(be_empty)

    with it('accepts phone numbers'):
      expect(self.first(analyze_number._phone_number, 18006694373)).to(
          be_one_of(
              '1800nowhere',
              '1800no where',
              '1800now here',
          ))

  with description('positional'):
    with it('rejects short positional numbers'):
      expect(self.run(analyze_number._positional, 3)).to(be_empty)

    with it('rejects positional with duplicated numbers'):
      expect(self.run(
          analyze_number._positional,
          12345678901234567890123456,
      )).to(be_empty)

    with it('accepts positional'):
      expect(self.first(
          analyze_number._positional,
          23100000000000000000000000,
      )).to(equal('cab'))

  with description('runlength'):
    with it('rejects random input'):
      expect(self.run(analyze_number._runlength, 651322333143)).to(be_empty)

    with it('accepts input'):
      # 11000000000000000111111111111111 = boo
      expect(self.first(analyze_number._runlength, 3221258239, 2)).to(
          equal('boo'))

    with it('accepts delimited input'):
      # 1101111111111111110111111111111111
      expect(self.first(analyze_number._runlength, 15032352767, 2)).to(
          equal('boo'))

  with description('t9'):
    with it('accepts t9'):
      expect(self.first(analyze_number._t9, 6669555)).to(equal('owl'))

    with it('rejects invalid t9'):
      expect(self.run(analyze_number._t9, 666666)).to(be_empty)

  with description('solutions'):
    with before.all:
      def solutions(n):
        (solution, weight), notes = next(analyze_number.solutions_with_notes(n))
        return solution, notes


      self.solutions = solutions

    with it('ignores empty input'):
      expect(analyze_number.solutions(0)).to(be_empty)

    with it('solves alphabet'):
      expect(self.solutions(312)).to(equal(('cab', ['base10'])))

    with it('solves ascii nibbles'):
      expect(self.solutions(0x6f776c)).to(equal(('owl', ['base16'])))

    with it('solves base 36'):
      expect(self.solutions(0xCAB)).to(equal(('cab', ['base16'])))

    with it('solves braille'):
      expect(self.solutions(135024560123)).to(equal(('owl', ['base10'])))

    with it('solves morse'):
      expect(self.solutions(222012201211)).to(equal(('owl', ['base10'])))

    with it('solves positional'):
      expect(self.solutions(23100000000000000000000000)).to(
          equal(('cab', ['base10'])))

    with it('solves hexspeak'):
      expect(self.solutions(0xDEAD)).to(equal(('dead', ['base16'])))

    with it('solves keyboard intersection'):
      expect(self.solutions(361358)).to(equal(('cab', ['base10'])))

    with it('solves lexicographical ordering'):
      expect(self.solutions(102012021)).to(equal(('cab', ['base10'])))

    with it('solves runlength'):
      expect(self.solutions(15032352767)).to(equal(('boo', ['base2'])))

    with it('solves t9'):
      expect(self.solutions(6669555)).to(equal(('owl', ['base10'])))

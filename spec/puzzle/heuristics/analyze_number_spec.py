from puzzle.heuristics import analyze_number
from spec.mamba import *

with description('analyze_number'):
  with before.each:
    def run(fn, n, base):
      digits = analyze_number._get_digits_in_base(n, base)
      min_digit = min(digits)
      max_digit = max(digits)
      for result in fn(digits, min_digit, max_digit):
        yield result


    def first(fn, n, base):
      return next(run(fn, n, base))


    self.run = lambda fn, n, base=10: call(run, fn, n, base)
    self.first = lambda fn, n, base=10: call(first, fn, n, base)

  with description('alphabet'):
    with it('rejects invalid input'):
      expect(self.run(analyze_number._alphabet, 101)).to(be_empty)

    with it('accepts input'):
      expect(self.first(analyze_number._alphabet, 312)).to(equal(('cab', 1)))

  with description('ascii_nibbles'):
    with it('accepts input'):
      expect(self.first(analyze_number._ascii_nibbles, 0x6f776c, 16)).to(
          equal(('owl', 1)))

    with it('accepts delimited input'):
      expect(next(analyze_number._ascii_nibbles([
        0x6, 0xf, 16, 0x7, 0x7, 16, 0x6, 0xc,
      ], 6, 16))).to(equal(('owl', 1)))

  with description('braille'):
    with it('rejects decreasing input'):
      expect(self.run(analyze_number._braille, 6543)).to(be_empty)

    with it('accepts increasing input'):
      expect(self.first(analyze_number._braille, 135024560123)).to(
          equal(('owl', 1)))

  with description('hex'):
    with it('understands hexspeak'):
      expect(self.first(analyze_number._hexspeak, 0xDEAD, 16)).to(
          equal(('dead', 1)))

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
        expect(self.first(analyze_number._morse, owl)).to(equal(('owl', 1)))

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
          equal(('1800nowhere', 1)))

  with description('t9'):
    with it('accepts t9'):
      expect(self.first(analyze_number._t9, 6669555)).to(equal(('owl', 1)))

    with it('rejects invalid t9'):
      expect(self.run(analyze_number._t9, 666666)).to(be_empty)

  with description('solutions'):
    with it('ignores empty input'):
      expect(analyze_number.solutions(0)).to(be_empty)

    with it('solves alphabet'):
      expect(next(analyze_number.solutions(312))).to(equal(('cab', 1)))

    with it('solves ascii nibbles'):
      expect(next(analyze_number.solutions(0x6f776c))).to(equal(('owl', 1)))

    with it('solves braille'):
      expect(next(analyze_number.solutions(135024560123))).to(equal(('owl', 1)))

    with it('solves morse'):
      expect(next(analyze_number.solutions(222012201211))).to(equal(('owl', 1)))

    with it('solves hexspeak'):
      expect(next(analyze_number.solutions(0xDEAD))).to(equal(('dead', 1)))

    with it('solves t9'):
      expect(next(analyze_number.solutions(6669555))).to(equal(('owl', 1)))

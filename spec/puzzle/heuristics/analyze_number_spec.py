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


    self.run = lambda fn, n, base=10: call(run, fn, n, base)


    def first(fn, n, base):
      return next(run(fn, n, base))


    self.first = lambda fn, n, base=10: call(first, fn, n, base)

  with it('ignores empty input'):
    expect(analyze_number.solutions(0)).to(be_empty)

  with description('hex'):
    with it('understands hexspeak'):
      expect(self.first(analyze_number._hexspeak, 0xDEAD, 16)).to(
          equal(('dead', 1)))

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
      expect(list(self.run(analyze_number._t9, 666666))).to(equal([]))

  with description('solutions'):
    with it('understands hexspeak'):
      expect(next(analyze_number.solutions(0xDEAD))).to(equal(('dead', 1)))

    with it('solves t9'):
      expect(next(analyze_number.solutions(6669555))).to(equal(('owl', 1)))

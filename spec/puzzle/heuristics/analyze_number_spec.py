from puzzle.heuristics import analyze_number
from spec.mamba import *

with description('analyze_number'):
  with it('ignores empty input'):
    expect(list(analyze_number.solutions(0))).to(equal([]))

  with description('hex'):
    with it('understands hexspeak'):
      expect(next(analyze_number._hexspeak([0xD, 0xE, 0xA, 0xD], 0xA, 0xE))).to(
          equal(('dead', 1)))

  with description('t9'):
    with it('accepts t9'):
      expect(next(analyze_number._t9([6, 6, 6, 9, 5, 5, 5], 5, 9))).to(
          equal(('owl', 1)))

    with it('rejects invalid t9'):
      expect(list(analyze_number._t9([6, 6, 6, 6, 6, 6, 6], 0, 0))).to(
          equal([]))

  with description('solutions'):
    with it('understands hexspeak'):
      expect(next(analyze_number.solutions(0xDEAD))).to(equal(('dead', 1)))

    with it('solves t9'):
      expect(next(analyze_number.solutions(6669555))).to(equal(('owl', 1)))

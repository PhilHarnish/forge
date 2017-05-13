from puzzle.heuristics import analyze_number
from spec.mamba import *

with description('analyze_number'):
  with it('ignores empty input'):
    expect(list(analyze_number.solutions(0))).to(equal([]))

  with it('understands hexspeak'):
    expect(next(analyze_number.solutions(0xDEAD))).to(equal(('dead', 1)))

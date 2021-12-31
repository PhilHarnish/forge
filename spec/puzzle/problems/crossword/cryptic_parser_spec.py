from puzzle.problems.crossword import cryptic_parser
from spec.mamba import *

with description('cryptic_parser'):
  with it('parses example'):
    expect(calling(
        cryptic_parser.parse, """No peg's turned into bathroom item? (6)""")
    ).not_to(raise_error)

import collections

from data import data
from puzzle.problems.crossword import cryptic_problem
from spec.mamba import *

with description('CrypticCrosswordProblem'):
  with it('ignores empty and garbage input'):
    expect(cryptic_problem.CrypticProblem.score([''])).to(equal(0))

  with it('rejects multiple lines'):
    expect(cryptic_problem.CrypticProblem.score(
        ['A quick brown', 'fox', 'jumps over the lazy dog'])).to(equal(0))

  with it('scores 1 word very low'):
    expect(cryptic_problem.CrypticProblem.score(['$#7'])).to(be_below(.25))

  with it('matches clues with (##) at the end'):
    expect(cryptic_problem.CrypticProblem.score(
        ['Example crossword clue (7)'])).to(be_between(.5, 1))

  with it('ambiguously matches clues with lots of words'):
    expect(cryptic_problem.CrypticProblem.score(
        ['A quick brown fox jumps over the lazy dog'])).to(be_above(.25))

  with it('matches data from fixtures'):
    fixtures = data.load(
        'data/puzzle_fixtures.txt',
        collections.namedtuple('fixture', 'name lines'))
    for line in fixtures['cryptic_crossword_clues'].lines:
      # Grr... Errors on this line are impossible to debug.
      c = call(cryptic_problem.CrypticProblem.score, [line])
      expect(c).to(be_above(.5))

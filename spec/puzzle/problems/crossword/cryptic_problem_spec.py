from data import data
from puzzle.problems.crossword import cryptic_problem
from spec.mamba import *


class CrypticFixture(object):
  def __init__(self, name, lines):
    self.clue, self.method = lines[:2]

with description('CrypticCrosswordProblem'):
  with before.all:
    self.fixtures = data.load('data/cryptic_clues.txt', CrypticFixture)

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

  with it('positively matches clues with cryptic indicators'):
    expect(cryptic_problem.CrypticProblem.score(
        ['Awful scene about right PC etc. display'])).to(equal(1))

  with it('is not fooled by substring matches'):
    expect(cryptic_problem.CrypticProblem.score(
        ['Winner or advocate (4|2))'])).to(be_between(0, 1))

  with it('ambiguously matches clues with lots of words'):
    expect(cryptic_problem.CrypticProblem.score(
        ['A quick brown fox jumps over the lazy dog'])).to(be_above(.25))

  with it('matches data from fixtures'):
    for word, fixture in self.fixtures.items():
      c = call(cryptic_problem.CrypticProblem.score, [fixture.clue])
      expect(c).to(be_above(.5))

from data import data
from puzzle.problems.crossword import cryptic_problem
from spec.mamba import *


class CrypticFixture(object):
  def __init__(self, name, lines):
    self.name = name
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
    for _, fixture in self.fixtures.items():
      c = call(cryptic_problem.CrypticProblem.score, [fixture.clue])
      expect(c).to(be_above(.5))

  with description('solutions'):
    with before.all:
      self.problems = {}
      for fixture in self.fixtures.values():
        self.problems[fixture.name] = cryptic_problem.CrypticProblem(
            fixture.name, [fixture.clue])

    with it('solves amsterdam'):
      expect(self.problems).to(have_key('AMSTERDAM'))
      expect(self.problems['AMSTERDAM'].solutions()).to(have_len(1))
      characters = set(self.problems['AMSTERDAM'].solutions().peek())
      expect(characters).to(equal(set('amsterdam')))

    with it('solves waste'):
      expect(self.problems).to(have_key('WASTE'))
      expect(self.problems['WASTE'].solutions()).not_to(be_empty)
      expect(self.problems['WASTE'].solutions()).to(have_key('waste'))

    with it('solves nemesis'):
      expect(self.problems).to(have_key('NEMESIS'))
      expect(self.problems['NEMESIS'].solutions()).not_to(be_empty)
      # TODO: Actually anagram this thing.
      expect(self.problems['NEMESIS'].solutions()).to(have_key('senseim'))

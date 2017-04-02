import collections
from unittest import mock

from expects import *

from src.data import data
from src.puzzle.problems import crossword_problem


with description('CrosswordProblem'):
  with it('ignores empty and garbage input'):
    expect(crossword_problem.CrosswordProblem.score('')).to(equal(0))

  with it('scores 1 word very low'):
    expect(crossword_problem.CrosswordProblem.score('$#!7')).to(be_below(.25))

  with it('positively matches clues with (##) at the end'):
    expect(crossword_problem.CrosswordProblem.score(
        'Example crossword clue (7)')).to(equal(1))

  with it('ambiguously matches clues with lots of words'):
    expect(crossword_problem.CrosswordProblem.score(
        'A quick brown fox jumps over the lazy dog')).to(be_above(.25))

  with it('matches data from fixtures'):
    fixtures = data.load(
        'data/puzzle_fixtures.txt',
        collections.namedtuple('fixture', 'name lines'))
    for line in fixtures['crossword_clues'].lines:
      expect(crossword_problem.CrosswordProblem.score(line)).to(be_above(.5))

  with context('constraints'):
    with it('constrains to fixed lengths'):
      problem = crossword_problem.CrosswordProblem('ex', ['example (3)'])
      problem._solve = mock.Mock(return_value={'a': 1, 'aa': .75, 'aaa': .5})
      expect(problem.solutions()).to(equal({'aaa': .5}))

  with context('solutions'):
    with it('queries for crossword solutions'):
      problem = crossword_problem.CrosswordProblem(
          'ex',
          ['Ask a question (5)'])
      solutions = problem.solutions()
      solution, weight = solutions.first()
      expect(solution).to(equal('query'))
      expect(weight).to(be_above(0))

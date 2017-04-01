from expects import *

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

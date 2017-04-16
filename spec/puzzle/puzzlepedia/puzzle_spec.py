import textwrap
from expects import *

from src.puzzle.heuristics import analyze
from src.puzzle.problems import problem
from src.puzzle.puzzlepedia import puzzle


class TestProblem(problem.Problem):
  @staticmethod
  def score(src):
    del src
    return 1

  def _solve(self):
    return {', '.join(self.lines): 1}

class WeakMatchProblem(problem.Problem):
  @staticmethod
  def score(src):
    del src
    return 0.1


with description('Puzzle'):
  with before.all:
    analyze.register(TestProblem)
    analyze.register(WeakMatchProblem)

  with after.all:
    analyze.reset()

  with it('instantiates'):
    expect(puzzle.Puzzle('')).not_to(be_none)

  with it('selects the best matching problem'):
    p = puzzle.Puzzle('sample')
    expect(p.problems()[0]).to(be_a(TestProblem))
    expect(p.problems()[0].kind).to(equal('TestProblem'))

  with it('selects the best solutions'):
    p = puzzle.Puzzle('sample')
    expect(p.solutions()).to(equal(['sample']))

  with context('multiple problems'):
    with it('finds multiple solutions'):
      p = puzzle.Puzzle(textwrap.dedent("""
           sample 1
           sample 2
       """))
      expect(p.solutions()).to(equal(['sample 1', 'sample 2']))


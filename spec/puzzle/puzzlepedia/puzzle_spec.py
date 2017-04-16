import textwrap
from expects import *

from src.puzzle.heuristics import analyze
from src.puzzle.problems import problem
from src.puzzle.puzzlepedia import puzzle


class TestProblem(problem.Problem):
  @staticmethod
  def score(src):
    del src
    return 0.9

  def _solve(self):
    return {'meta: '+ ''.join(self.lines): 1}


class WeakMatchProblem(problem.Problem):
  @staticmethod
  def score(src):
    del src
    return 0.1

  def _solve(self):
    return {'meta: weak match': 0.1}


class MetaProblem(problem.Problem):
  @staticmethod
  def score(src):
    if src.startswith('meta:'):
      return 1
    return 0

  def _solve(self):
    return {'final solution': 1}


def _get_multi_puzzle():
  return puzzle.Puzzle(textwrap.dedent("""
      sample 1
      sample 2
  """))


with description('Puzzle'):
  with before.all:
    analyze.register(TestProblem)
    analyze.register(WeakMatchProblem)
    analyze.register(MetaProblem)

  with after.all:
    analyze.reset()

  with it('instantiates from string'):
    expect(puzzle.Puzzle('')).not_to(be_none)

  with it('instantiates from list'):
    expect(puzzle.Puzzle([''])).not_to(be_none)

  with it('instantiates from Puzzle'):
    expect(puzzle.Puzzle(puzzle.Puzzle(''))).not_to(be_none)

  with it('rejects invalid input'):
    expect(lambda: puzzle.Puzzle(None)).to(raise_error(NotImplementedError))

  with it('selects the best matching problem'):
    p = puzzle.Puzzle('sample')
    expect(p.problems()[0]).to(be_a(TestProblem))
    expect(p.problems()[0].kind).to(equal('TestProblem'))

  with it('selects the best solutions'):
    p = puzzle.Puzzle('sample')
    expect(p.solutions()).to(equal(['meta: sample']))

  with context('multiple problems'):
    with it('finds multiple solutions'):
      p = _get_multi_puzzle()
      expect(p.solutions()).to(equal(['meta: sample 1', 'meta: sample 2']))

    with it('creates a second stage from the first'):
      stage2 = _get_multi_puzzle().get_next_stage()
      expect(stage2).to(be_a(puzzle.Puzzle))

    with it('finds the solution to the second stage'):
      stage2 = _get_multi_puzzle().get_next_stage()
      expect(stage2.solutions()).to(equal(['final solution'] * 2))

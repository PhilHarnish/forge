import textwrap

import mock

from spec.mamba import *

from puzzle.heuristics import analyze
from puzzle.problems import problem
from puzzle.puzzlepedia import puzzle


class TestProblem(problem.Problem):
  @staticmethod
  def score(lines):
    del lines
    return 0.9

  def _solve(self):
    return {'meta: '+ ''.join(self.lines): 1}


class WeakMatchProblem(problem.Problem):
  @staticmethod
  def score(lines):
    del lines
    return 0.1

  def _solve(self):
    return {'meta: weak match': 0.1}


class MetaProblem(problem.Problem):
  @staticmethod
  def score(lines):
    src = '\n'.join(lines)
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

  with it('allows solution override'):
    p = puzzle.Puzzle('sample')
    p.problem(0).solution = 'solution override'
    expect(p.solutions()).to(equal(['solution override']))

  with description('multiple problems'):
    with it('finds multiple solutions'):
      p = _get_multi_puzzle()
      expect(p.solutions()).to(equal(['meta: sample 1', 'meta: sample 2']))

    with it('creates a second stage from the first'):
      stage2 = _get_multi_puzzle().get_next_stage()
      expect(stage2).to(be_a(puzzle.Puzzle))

    with it('finds the solution to the second stage'):
      stage2 = _get_multi_puzzle().get_next_stage()
      expect(stage2.solutions()).to(equal(['final solution'] * 2))

  with description('async changes'):
    with it('notifies subscribers when first subscribing'):
      p = puzzle.Puzzle('sample')
      subs = mock.Mock()
      p.problem(0).subscribe(subs)
      expect(subs.on_next.call_args).to(equal(mock.call(p.problem(0))))

    with it('notifies problem subscribers when solution changes'):
      p = puzzle.Puzzle('sample')
      subs = mock.Mock()
      p.problem(0).subscribe(subs)
      expect(subs.on_next.call_count).to(equal(1))
      p.problem(0).solution = 'solution override'
      expect(subs.on_next.call_count).to(equal(2))

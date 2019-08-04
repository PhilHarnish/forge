from puzzle.problems import problem
from puzzle.puzzlepedia import meta_problem
from spec.mamba import *


class TestProblem1(problem.Problem):
  def __init__(self) -> None:
    super(TestProblem1, self).__init__('test', [])

  def _solve(self) -> dict:
    return {self.__class__.__name__: 1.0}


class TestProblem2(TestProblem1):
  pass


with description('meta_problem'):
  with it('constructs without error'):
    expect(calling(meta_problem.MetaProblem)).not_to(raise_error)

  with it('it holds instances of Problem'):
    mp = meta_problem.MetaProblem()
    mp[TestProblem1()] = 0.5
    mp[TestProblem2()] = 1.0
    expect(mp).to(have_len(2))

  with it('returns highest weighted instance'):
    mp = meta_problem.MetaProblem()
    mp[TestProblem1()] = 0.5
    mp[TestProblem2()] = 1.0
    expect(mp.active).to(be_a(TestProblem2))

  with it('returns solution highest weighted instance'):
    mp = meta_problem.MetaProblem()
    mp[TestProblem1()] = 0.5
    mp[TestProblem2()] = 1.0
    expect(mp.solution).to(equal('TestProblem2'))

  with it('accepts custom solutions'):
    mp = meta_problem.MetaProblem()
    mp.solution = 'example'
    expect(mp.solution).to(equal('example'))

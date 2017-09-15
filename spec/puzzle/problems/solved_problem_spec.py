from puzzle.problems import solved_problem
from spec.mamba import *

with description('SolvedProblem'):
  with it('ignores empty input'):
    expect(solved_problem.SolvedProblem.score([''])).to(equal(0))

  with it('ignores multiple lines'):
    expect(solved_problem.SolvedProblem.score(['a', 'b'])).to(equal(0))

  with it('matches solved problems'):
    expect(solved_problem.SolvedProblem.score([
      'SOLUTION (clue)'
    ])).to(equal(1))

  with it('matches multiple solutions, "," delimited'):
    expect(solved_problem.SolvedProblem.score([
      'SOLUTION 1, SOLUTION 2 (clue)'
    ])).to(equal(1))

  with it('matches multiple solutions, "/" delimited'):
    expect(solved_problem.SolvedProblem.score([
      'SOLUTION 1 / SOLUTION 2 (clue)'
    ])).to(equal(1))

  with it('allows whitespace'):
    expect(solved_problem.SolvedProblem.score([
      'GONE WITH THE WIND (clue)'
    ])).to(equal(1))

  with it('allows lowercase with --'):
    expect(solved_problem.SolvedProblem.score([
      'Gone with the wind -- (clue)'
    ])).to(equal(1))

  with description('solutions'):
    with it('returns provided solutions'):
      p = solved_problem.SolvedProblem('ex', ['SOLUTION (clue)'])
      expect(p.solutions()).to(equal({
        'SOLUTION': 1,
      }))

    with it('returns all provided solutions'):
      p = solved_problem.SolvedProblem('ex', ['SOLUTION 1 / SOLUTION 2 (clue)'])
      expect(p.solutions()).to(equal({
        'SOLUTION 1': 1,
        'SOLUTION 2': 1,
      }))

    with it('removes ( and ) from clue'):
      p = solved_problem.SolvedProblem('ex', ['SOLUTION (clue)'])
      expect(p.lines).to(equal(['clue']))

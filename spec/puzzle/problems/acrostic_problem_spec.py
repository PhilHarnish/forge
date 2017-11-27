from puzzle.problems import acrostic_problem
from spec.mamba import *

with description('AcrosticProblem'):
  with it('ignores empty and garbage input'):
    expect(acrostic_problem.AcrosticProblem.score([''])).to(equal(0))

  with it('rejects one line'):
    expect(acrostic_problem.AcrosticProblem.score(
        ['A quick brown fox jumps over the lazy dog'])).to(equal(0))

  with it('scores lines with multiple words low'):
    expect(acrostic_problem.AcrosticProblem.score([
        'dog house', 'cat', 'bat',
    ])).to(be_below(acrostic_problem.AcrosticProblem.score([
        'doghouse', 'cat', 'bat',
    ])))

  with it('positively matches acrostic with indexes'):
    expect(acrostic_problem.AcrosticProblem.score([
      '@ 1 2', 'babbling', 'bachelor'
    ])).to(equal(1))

  with it('favors words with similar lengths'):
    expect(acrostic_problem.AcrosticProblem.score([
      'babbling', 'bachelor', 'backbone', 'backward', 'bacteria',
      'baffling', 'balanced', 'baldness', 'ballroom', 'bankrupt',
    ])).to(equal(1))

  with it('penalizes few words'):
    expect(acrostic_problem.AcrosticProblem.score([
        'babbling', 'bachelor', 'backbone',
    ])).to(be_below(1))

  with description('indexed solutions'):
    with it('finds specified solutions'):
      problem = acrostic_problem.AcrosticProblem('test',
          [
            '@ 1 2 3',
            'CAB',
            'CAB',
            'CAB',
          ]
      )
      expect(list(problem.solutions())).to(equal(['cab']))

    with it('finds specified solutions with permutation'):
      problem = acrostic_problem.AcrosticProblem('test',
          [
            '@ 1 2 3',
            '* xxB',
            '* xAx',
            '* Cxx',
          ]
      )
      expect(list(problem.solutions())).to(equal(['cab']))

    with it('finds specified solutions with permutation and 1 unknown index'):
      problem = acrostic_problem.AcrosticProblem('test',
          [
            '@ 1 2 ?',
            '* xAB',
            '* xAT',
            '* Cxx',
          ]
      )
      expect(list(problem.solutions())).to(equal(['cat', 'cab']))

from data import warehouse
from puzzle.problems import acrostic_problem
from puzzle.puzzlepedia import prod_config
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

with description('regression tests'):
  with before.all:
    warehouse.save()
    prod_config.init()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('terminates eventually'):
    text = 'ENJOYDANDDORSIMULATE'
    problem = acrostic_problem.AcrosticProblem('test', [c for c in text])
    expect(list(problem.solutions())).to(equal([
      'enjoy dan d dor simulate', 'enjoy dan d dor simula t e',
      'enjoy dan d dor simula te', 'enjoy dan d dor simul a te',
      'enjoy dan d dor simul at e', 'enjoy dan d dor simul ate',
      'enjoy dan d dor simu late', 'enjoy dan d dor simu lat e',
      'enjoy dan d dor simu la te', 'enjoy dan ddo rsi mula t e',
      'enjoy dan ddo rsi mula te', 'enjoy dan ddo rsi mul a te',
      'enjoy dan ddo rsi mul at e', 'enjoy dan ddo rsi mul ate',
      'enjoy dan ddo r simulate', 'enjoy dan ddo r simula t e',
      'enjoy dan ddo r simula te', 'enjoy dan ddo r simul a te',
      'enjoy dan ddo r simul at e', 'enjoy dan ddo r simul ate',
      'enjoy dan ddo r simu late', 'enjoy dan ddo r simu lat e',
      'enjoy dan ddo r simu la te', 'enjoy dan dd or simulate',
      'enjoy dan dd or simula t e', 'enjoy dan dd or simula te',
      'enjoy dan dd or simul a te', 'enjoy dan dd or simul at e',
      'enjoy dan dd or simul ate', 'enjoy dan dd or simu late',
      'enjoy dan dd or simu lat e', 'enjoy dan dd or simu la te',
      'enjoy dan dd orsi mula t e', 'enjoy dan dd orsi mula te',
      'enjoy dan dd orsi mul a te', 'enjoy dan dd orsi mul at e',
      'enjoy dan dd orsi mul ate', 'enjoy da nd dor simulate',
      'enjoy da nd dor simula t e', 'enjoy da nd dor simula te',
      'enjoy da nd dor simul a te', 'enjoy da nd dor simul at e',
      'enjoy da nd dor simul ate', 'enjoy da nd dor simu late',
      'enjoy da nd dor simu lat e', 'enjoy da nd dor simu la te',
      'enjoy d and dor simulate', 'enjoy d and dor simula t e',
      'enjoy d and dor simula te', 'enjoy d and dor simul a te',
      'enjoy d and dor simul at e', 'enjoy d and dor simul ate',
      'enjoy d and dor simu late', 'enjoy d and dor simu lat e',
      'enjoy d and dor simu la te', 'enjoy d andd or simulate',
      'enjoy d andd or simula t e', 'enjoy d andd or simula te',
      'enjoy d andd or simul a te', 'enjoy d andd or simul at e',
      'enjoy d andd or simul ate', 'enjoy d andd or simu late',
      'enjoy d andd or simu lat e', 'enjoy d andd or simu la te',
      'enjoy d andd orsi mula t e', 'enjoy d andd orsi mula te',
      'enjoy d andd orsi mul a te', 'enjoy d andd orsi mul at e',
      'enjoy d andd orsi mul ate'
    ]))

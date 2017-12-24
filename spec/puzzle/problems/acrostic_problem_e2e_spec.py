from data import warehouse
from puzzle.problems import acrostic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with description('acrostic end2end tests', 'end2end'):
  with before.all:
    warehouse.save()
    prod_config.init()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('finds saxophones'):
    problem = acrostic_problem.AcrosticProblem(
        'test',
        textwrap.dedent("""
          @ 1 2 3 4 5 6 7 8 9 10
          * BigOldBell
          * BootyJuker
          * CorkChoker
          * FacePinner
          * FakeTurtle
          * LemurPoker
          * PixieProng
          * SheepStick
          * SqueezeToy
          * TinyStools
        """.lower()).strip().split('\n')
    )
    expect(problem.solution).to(equal('saxophones'))

  with it('terminates eventually'):
    text = 'ENJOYDANDDORSIMULATE'
    problem = acrostic_problem.AcrosticProblem('test', [c for c in text])
    expect(list(sorted(problem.solutions()))).to(equal([
      'enjoy d and dor simu la te', 'enjoy d and dor simu lat e',
      'enjoy d and dor simu late', 'enjoy d and dor simul a te',
      'enjoy d and dor simul at e', 'enjoy d and dor simul ate',
      'enjoy d and dor simula t e', 'enjoy d and dor simula te',
      'enjoy d and dor simulate', 'enjoy d andd or simu la te',
      'enjoy d andd or simu lat e', 'enjoy d andd or simu late',
      'enjoy d andd or simul a te', 'enjoy d andd or simul at e',
      'enjoy d andd or simul ate', 'enjoy d andd or simula t e',
      'enjoy d andd or simula te', 'enjoy d andd or simulate',
      'enjoy d andd orsi mul a te', 'enjoy d andd orsi mul at e',
      'enjoy d andd orsi mul ate', 'enjoy d andd orsi mula t e',
      'enjoy d andd orsi mula te', 'enjoy da nd dor simu la te',
      'enjoy da nd dor simu lat e', 'enjoy da nd dor simu late',
      'enjoy da nd dor simul a te', 'enjoy da nd dor simul at e',
      'enjoy da nd dor simul ate', 'enjoy da nd dor simula t e',
      'enjoy da nd dor simula te', 'enjoy da nd dor simulate',
      'enjoy dan d dor simu la te', 'enjoy dan d dor simu lat e',
      'enjoy dan d dor simu late', 'enjoy dan d dor simul a te',
      'enjoy dan d dor simul at e', 'enjoy dan d dor simul ate',
      'enjoy dan d dor simula t e', 'enjoy dan d dor simula te',
      'enjoy dan d dor simulate', 'enjoy dan dd or simu la te',
      'enjoy dan dd or simu lat e', 'enjoy dan dd or simu late',
      'enjoy dan dd or simul a te', 'enjoy dan dd or simul at e',
      'enjoy dan dd or simul ate', 'enjoy dan dd or simula t e',
      'enjoy dan dd or simula te', 'enjoy dan dd or simulate',
      'enjoy dan dd orsi mul a te', 'enjoy dan dd orsi mul at e',
      'enjoy dan dd orsi mul ate', 'enjoy dan dd orsi mula t e',
      'enjoy dan dd orsi mula te', 'enjoy dan ddo r simu la te',
      'enjoy dan ddo r simu lat e', 'enjoy dan ddo r simu late',
      'enjoy dan ddo r simul a te', 'enjoy dan ddo r simul at e',
      'enjoy dan ddo r simul ate', 'enjoy dan ddo r simula t e',
      'enjoy dan ddo r simula te', 'enjoy dan ddo r simulate',
      'enjoy dan ddo rsi mul a te', 'enjoy dan ddo rsi mul at e',
      'enjoy dan ddo rsi mul ate', 'enjoy dan ddo rsi mula t e',
      'enjoy dan ddo rsi mula te']))


from puzzle.problems import cryptogram_problem
from spec.data import fixtures
from spec.mamba import *

with description('CryptogramProblem'):
  with it('ignores empty input'):
    expect(cryptogram_problem.CryptogramProblem.score([''])).to(equal(0))

  with it('rejects purely non-word inputs'):
    expect(cryptogram_problem.CryptogramProblem.score(['$#!7'])).to(equal(0))

  with it('favors jibberish'):
    expect(cryptogram_problem.CryptogramProblem.score([
      'asdf', 'fdsa', 'thesearenot', 'intest', 'dictionary',
    ])).to(equal(1))

  with it('accepts all other input'):
    expect(cryptogram_problem.CryptogramProblem.score(['owl'])).to(
        be_between(0, .25))

  with description('basic solutions'):
    with before.all:
      fixtures.init()

    with it('solves rot13'):
      p = cryptogram_problem.CryptogramProblem('rot13', ['bjy'])
      expect(p.solutions()).to(equal({'owl': 1}))

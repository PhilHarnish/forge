from puzzle.problems import cryptogram_problem
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

from puzzle.problems import cryptogram_problem
from spec.mamba import *

with description('CryptogramProblem'):
  with it('ignores empty input'):
    expect(cryptogram_problem.CryptogramProblem.score([''])).to(equal(0))

  with it('accepts all other input'):
    expect(cryptogram_problem.CryptogramProblem.score(['asdf'])).to(be_above(0))

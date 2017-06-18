from puzzle.problems import logic_problem
from spec.mamba import *

with description('LogicProblem'):
  with it('ignores empty input'):
    expect(logic_problem.LogicProblem.score([''])).to(equal(0))

  with it('rejects a single line'):
    expect(logic_problem.LogicProblem.score(['a single line'])).to(equal(0))

  with it('assigns a non-zero score to many lines'):
    expect(logic_problem.LogicProblem.score([
      'this', 'is', 'many', 'lines',
    ])).to(be_above(0))

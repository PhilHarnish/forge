from data import warehouse
from puzzle.problems import number_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with description('NumberProblem'):
  with it('ignores empty input'):
    expect(number_problem.NumberProblem.score([''])).to(equal(0))

  with it('rejects multiple lines'):
    expect(number_problem.NumberProblem.score(['1', '2', '3'])).to(equal(0))

  with it('rejects pseudo-numbers'):
    expect(number_problem.NumberProblem.score(['1.2.3'])).to(equal(0))

  with it('accepts integers'):
    expect(number_problem.NumberProblem.score(['123'])).to(be_above(0))

  with it('accepts floats'):
    expect(number_problem.NumberProblem.score(['1.23'])).to(be_above(0))

  with it('accepts hex'):
    expect(number_problem.NumberProblem.score(['0xDEADBEEF'])).to(be_above(0))

  with it('accepts octal'):
    expect(number_problem.NumberProblem.score(['0777'])).to(be_above(0))

  with it('reluctantly accepts 0'):
    expect(number_problem.NumberProblem.score(['0'])).to(be_between(0, .000001))

  with it('favors data with more information density'):
    expect(number_problem.NumberProblem.score(['1234'])).to(be_above(
        number_problem.NumberProblem.score(['123'])
    ))

  with _description('solutions'):
    with before.all:
      warehouse.save()
      prod_config.init()

    with after.all:
      prod_config.reset()
      warehouse.restore()

    with it('solves simple problems'):
      problem = number_problem.NumberProblem(
          'ex',
          ['0xCAB'])  # 6546
      solutions = problem.solutions()
      solution, weight = solutions.first()
      expect(solution).to(equal('cab'))
      expect(weight).to(be_above(0))

    with it('solves real problems with increment'):
      problem = number_problem.NumberProblem(
          'BINARY +1',
          ['300451275870959962186'])
      solutions = problem.solutions()
      solution, weight = solutions.first()
      expect(solution).to(equal('binary +1'))
      expect(weight).to(be_above(0))

    with it('solves more problems with even more increment'):
      problem = number_problem.NumberProblem(
          'DECIMAL +25',
          ['29165720900'])
      solutions = problem.solutions()
      solution, weight = solutions.first()
      expect(solution).to(equal('decimal +25'))
      expect(weight).to(be_above(0))

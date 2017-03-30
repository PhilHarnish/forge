from expects import *

from src.puzzle.problems import problem
from src.puzzle.heuristics import analyze


class ExampleProblemZeroes(problem.Problem):
  @staticmethod
  def score(src):
    return src.count('0') / len(src)


class ExampleProblemOnes(problem.Problem):
  @staticmethod
  def score(src):
    return src.count('1') / len(src)


with description('identify'):
  with it('is a no-op without problem types registered'):
    expect(analyze.identify('')).to(be_empty)

  with context('ExampleProblem'):
    with before.all:
      problem.register(ExampleProblemZeroes)
      problem.register(ExampleProblemOnes)

    with after.all:
      problem.unregister_all()

    with it('matches unambiguous results'):
      result = analyze.identify('0000')
      expect(result).to(equal({ExampleProblemZeroes: 1}))

    with it('match ambiguous results'):
      result = analyze.identify('0011')
      expect(result).to(equal({
        ExampleProblemZeroes: .5,
        ExampleProblemOnes: .5,
      }))

    with it('match order results'):
      result = analyze.identify('0111')
      expect(tuple(result.items())).to(equal((
          (ExampleProblemOnes, .75),
          (ExampleProblemZeroes, .25),
      )))

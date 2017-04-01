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


with description('register'):
  with after.each:
    analyze.reset()

  with it('registers types'):
    class Example(object):
      pass
    analyze.register(Example)
    expect(analyze.problem_types()).to(equal({Example}))


with description('identify'):
  with it('is a no-op without problem types registered'):
    expect(analyze.identify('')).to(be_empty)

  with context('ExampleProblem'):
    with before.all:
      analyze.register(ExampleProblemZeroes)
      analyze.register(ExampleProblemOnes)

    with after.all:
      analyze.reset()

    with it('matches unambiguous results'):
      result = analyze.identify('0000')
      expect(result).to(have_key(ExampleProblemZeroes))
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

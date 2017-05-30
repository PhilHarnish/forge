from puzzle.heuristics import analyze
from puzzle.problems import anagram_problem, problem
from puzzle.problems.crossword import crossword_problem, cryptic_problem
from spec.mamba import *


class ExampleProblemZeroes(problem.Problem):
  @staticmethod
  def score(lines):
    src = '\n'.join(lines)
    return src.count('0') / len(src)


class ExampleProblemOnes(problem.Problem):
  @staticmethod
  def score(lines):
    src = '\n'.join(lines)
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
      result = analyze.identify(['0000'])
      expect(result).to(have_key(ExampleProblemZeroes))
      expect(result).to(equal({ExampleProblemZeroes: 1}))

    with it('match ambiguous results'):
      result = analyze.identify(['0011'])
      expect(result).to(equal({
        ExampleProblemZeroes: .5,
        ExampleProblemOnes: .5,
      }))

    with it('match order results'):
      result = analyze.identify(['0111'])
      expect(tuple(result.items())).to(equal((
          (ExampleProblemOnes, .75),
          (ExampleProblemZeroes, .25),
      )))

  with context('all supported problems'):
    with before.all:
      analyze.init()

    with after.all:
      analyze.reset()

    with it('identifies crossword examples'):
      identified = analyze.identify(['A type of puzzle (9)'])
      expect(identified).to(have_key(crossword_problem.CrosswordProblem))
      expect(identified[crossword_problem.CrosswordProblem]).to(equal(1))

    with it('identifies anagrams'):
      identified = analyze.identify(['snap'])
      expect(identified).to(have_key(anagram_problem.AnagramProblem))
      expect(identified[anagram_problem.AnagramProblem]).to(equal(1))

    with it('identifies (and prefers) cryptic problems over crosswords'):
      identified = analyze.identify(['Lizard, good with Coke, oddly (5)'])
      expect(identified).to(have_key(cryptic_problem.CrypticProblem))
      expect(identified).to(have_key(crossword_problem.CrosswordProblem))
      expect(identified[cryptic_problem.CrypticProblem]).to(equal(1))
      expect(identified[cryptic_problem.CrypticProblem]).to(be_above(
          identified[crossword_problem.CrosswordProblem]))

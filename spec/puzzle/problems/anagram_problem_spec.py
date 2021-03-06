from puzzle.problems import anagram_problem
from spec.mamba import *

with description('AnagramProblem'):
  with it('ignores empty and garbage input'):
    expect(anagram_problem.AnagramProblem.score([''])).to(equal(0))

  with it('rejects multiple lines'):
    expect(anagram_problem.AnagramProblem.score(
        'A quick brown fox jumps over the lazy dog'.split())).to(equal(0))

  with it('accepts anagrams'):
    expect(anagram_problem.AnagramProblem.score(['snap'])).to(equal(1))

  with description('problem instance'):
    with before.each:
      self.subject = anagram_problem.AnagramProblem('example', ['snap'])

    with it('solves anagrams'):
      expect(list(self.subject.solutions().items())).to(equal([
        ('snap', 1.0),
        ('naps', 0.5),
      ]))

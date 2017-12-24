from puzzle.heuristics import analyze
from puzzle.problems import problem
from puzzle.puzzlepedia import puzzle
from spec.mamba import *


class TestProblem(problem.Problem):
  @staticmethod
  def score(lines):
    if len(lines) > 1:
      return 0
    return 0.9

  def _solve(self):
    return {'meta: '+ ''.join(self.lines): 1}


class WeakMatchProblem(problem.Problem):
  @staticmethod
  def score(lines):
    del lines
    return 0.1

  def _solve(self):
    return {'meta: weak match': 0.1}


class MetaProblem(problem.Problem):
  @staticmethod
  def score(lines):
    src = '\n'.join(lines)
    if src.startswith('meta:'):
      return 1
    return 0

  def _solve(self):
    return {'final solution': 1}


def _get_multi_puzzle():
  return puzzle.Puzzle('multi-puzzle', textwrap.dedent("""
      sample 1
      sample 2
  """))


with description('Puzzle'):
  with before.all:
    analyze.reset()  # https://github.com/nestorsalceda/mamba/issues/91
    analyze.register(TestProblem)
    analyze.register(WeakMatchProblem)
    analyze.register(MetaProblem)

  with after.all:
    analyze.reset()

  with it('instantiates from string'):
    expect(puzzle.Puzzle('empty', '')).not_to(be_none)

  with it('instantiates from list'):
    expect(puzzle.Puzzle('empty', [''])).not_to(be_none)

  with it('instantiates from Puzzle'):
    expect(puzzle.Puzzle('empty', puzzle.Puzzle('child', ''))).not_to(be_none)

  with it('rejects invalid input'):
    expect(lambda: puzzle.Puzzle('empty', None)).to(
        raise_error(NotImplementedError))

  with it('selects the best matching problem'):
    p = puzzle.Puzzle('sample', 'sample')
    expect(p.problems()[0]).to(be_a(TestProblem))
    expect(p.problems()[0].kind).to(equal('TestProblem'))

  with it('selects the best solutions'):
    p = puzzle.Puzzle('sample', 'sample')
    expect(p.solutions()).to(equal(['meta: sample']))

  with it('allows solution override'):
    p = puzzle.Puzzle('sample', 'sample')
    p.problem(0).solution = 'solution override'
    expect(p.solutions()).to(equal(['solution override']))

  with description('multiple problems'):
    with it('finds multiple solutions'):
      p = _get_multi_puzzle()
      expect(p.solutions()).to(equal(['meta: sample 1', 'meta: sample 2']))

    with it('creates a second stage from the first'):
      stage2 = _get_multi_puzzle().get_next_stage()
      expect(stage2).to(be_a(puzzle.Puzzle))

    with it('finds the solution to the second stage'):
      stage2 = _get_multi_puzzle().get_next_stage()
      expect(stage2.solutions()).to(equal(['final solution']))

  with description('async changes'):
    with it('notifies problem subscribers when solution changes'):
      p = puzzle.Puzzle('sample', 'sample')
      subs = mock.Mock()
      p.subscribe(subs)
      expect(subs.on_next.call_count).to(equal(0))
      p.problem(0).solution = 'solution override'
      expect(subs.on_next.call_count).to(equal(1))
      expect(subs.on_next.call_args).to(equal(mock.call(
          ('sample.0', p.problem(0))
      )))

  with description('regression tests'):
    with it('parses clues in order'):
      source = textwrap.dedent("""
        Classic Billy Wilder movie (4 wds)
        It ended with the Siege of Yorktown (2 wds)
        It may warn you of suprising object sizes (3 wds)
        Like most solid objects, as opposed to linear (hyph.)
        One who studies the spread of diseases
        The point in the orbit of a planet at which its closest to the sun
        Something asked intended to provoke a specific response (2 wds)
        Sort of valuable, like some gemstones
        Thoughtful discussion, as before a bill
      """).strip()
      lines = source.split('\n')
      p = puzzle.Puzzle('ex', source)
      expect(p.problems()).to(have_len(len(lines)))
      for problem, line in zip(p.problems(), lines):
        expect(problem.lines).to(equal([line]))

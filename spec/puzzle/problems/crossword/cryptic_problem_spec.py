from data import anagram_index, data, trie, warehouse
from puzzle.problems.crossword import cryptic_problem
from spec.mamba import *


class CrypticFixture(object):
  def __init__(self, name, lines):
    self.name = name
    self.clue, self.method = lines[:2]

with description('CrypticCrosswordProblem'):
  with before.all:
    self.fixtures = data.load('data/cryptic_clues.txt', CrypticFixture)

  with it('ignores empty and garbage input'):
    expect(cryptic_problem.CrypticProblem.score([''])).to(equal(0))

  with it('rejects multiple lines'):
    expect(cryptic_problem.CrypticProblem.score(
        ['A quick brown', 'fox', 'jumps over the lazy dog'])).to(equal(0))

  with it('scores 1 word very low'):
    expect(cryptic_problem.CrypticProblem.score(['$#7'])).to(be_below(.25))

  with it('matches clues with (##) at the end'):
    expect(cryptic_problem.CrypticProblem.score(
        ['Example crossword clue (7)'])).to(be_between(.5, 1))

  with it('positively matches clues with cryptic indicators'):
    expect(cryptic_problem.CrypticProblem.score(
        ['Awful scene about right PC etc. display'])).to(equal(1))

  with it('is not fooled by substring matches'):
    expect(cryptic_problem.CrypticProblem.score(
        ['Winner or advocate (4|2))'])).to(be_between(0, 1))

  with it('ambiguously matches clues with lots of words'):
    expect(cryptic_problem.CrypticProblem.score(
        ['A quick brown fox jumps over the lazy dog'])).to(be_above(.25))

  with it('matches data from fixtures'):
    for _, fixture in self.fixtures.items():
      c = call(cryptic_problem.CrypticProblem.score, [fixture.clue])
      expect(c).to(be_above(.5))

  with description('solutions'):
    with before.all:
      self.problems = {}
      all_clues = []
      for fixture in self.fixtures.values():
        all_clues.append(fixture.clue)
        self.problems[fixture.name] = cryptic_problem.CrypticProblem(
            fixture.name, [fixture.clue])
      expect(all_clues).to(have_len(26))  # Make fail to see output.
      warehouse.save()
      d = dict([
        (fixture.name.lower(), 100000) for fixture in self.fixtures.values()
      ])
      d['micro'] = 10000  # For MUSIC.
      d['witch'] = 10000  # For GECKO.
      d['wight'] = 10000  # For GECKO.
      warehouse.register('/words/unigram', d)
      t = trie.Trie(warehouse.get('/words/unigram').items())
      warehouse.register('/words/unigram/trie', t)
      a = anagram_index.AnagramIndex(warehouse.get('/words/unigram'))
      warehouse.register('/words/unigram/anagram_index', a)

    with after.all:
      warehouse.restore()

    with it('solves amsterdam'):
      expect(self.problems).to(have_key('AMSTERDAM'))
      expect(self.problems['AMSTERDAM'].solutions()).to(have_len(1))
      expect(self.problems['AMSTERDAM'].solutions()).to(have_key('amsterdam'))

    with it('solves waste'):
      expect(self.problems).to(have_key('WASTE'))
      expect(self.problems['WASTE'].solutions()).not_to(be_empty)
      expect(self.problems['WASTE'].solutions()).to(have_key('waste'))

    with it('solves nemesis'):
      expect(self.problems).to(have_key('NEMESIS'))
      expect(self.problems['NEMESIS'].solutions()).not_to(be_empty)
      expect(self.problems['NEMESIS'].solutions()).to(have_key('nemesis'))

    with it('solves gherkin'):
      expect(self.problems).to(have_key('GHERKIN'))
      expect(self.problems['GHERKIN'].solutions()).not_to(be_empty)
      expect(self.problems['GHERKIN'].solutions()).to(have_key('gherkin'))

    with it('solves music'):
      expect(self.problems).to(have_key('MUSIC'))
      solutions = self.problems['MUSIC'].solutions()
      expect(solutions).not_to(be_empty)
      expect(solutions).to(have_key('music'))
      expect(solutions).to(have_key('micro'))
      expect(solutions['music']).to(be_above(solutions['micro']))

    with it('solves gecko'):
      expect(self.problems).to(have_key('GECKO'))
      solutions = self.problems['GECKO'].solutions()
      expect(solutions).not_to(be_empty)
      expect(solutions).to(have_key('gecko'))
      expect(solutions).not_to(have_key('witch'))
      expect(solutions).to(have_key('wight'))
      expect(solutions['gecko']).to(be_above(solutions['wight']))

    with it('solves all problems'):
      incomplete = {
        # Requires synonyms.
        'CRAMPON', 'GREENBELT', 'PASTRY', 'START',
        # Requires crossword lookups.
        'ESCOURT', 'SLING', 'STEAK', 'TWIG',
        # Requires either.
        'DAMAGES', 'RUSHDIE', 'NOTE',
      }
      incomplete_seen = set()
      unsupported = set()
      unsupported_seen = set()
      results = {}
      for problem in self.problems:
        if problem in incomplete:
          incomplete_seen.add(problem)
          continue
        try:
          results[problem] = dict(self.problems[problem].solutions())
        except NotImplementedError:
          unsupported_seen.add(problem)
      expect(incomplete_seen).to(equal(incomplete))
      expect(unsupported_seen).to(equal(unsupported))
      expect(results).to(have_len(
          len(self.problems) - len(incomplete) - len(unsupported)))
      for problem, value in results.items():
        expect((problem, value)).not_to(equal((problem, {})))
        problem_lower = problem.lower()
        expect(value).to(have_key(problem_lower))
        expect(value[problem_lower]).to(equal(1))

from data import data, trie, warehouse
from data.anagram import anagram_index
from data.word_api import word_api
from puzzle.problems.crossword import cryptic_problem
from spec.mamba import *


ORIGINAL_UNSOLVED = """
[MONORAIL]
Correspondence on or inside train (8)
M(ONOR)AIL
"""


class CrypticFixture(object):
  def __init__(self, name: str, lines: List[str]) -> None:
    self.name = name
    self.clue, self.method = lines[:2]


with description('with wordnet', 'end2end') as self:
  with before.all:
    warehouse.save()
    warehouse.register('/api/words', word_api.get_api('wordnet'))
    self.problems = {}
    all_clues = []
    fixtures = data.load('data/cryptic_clues.txt', CrypticFixture)
    fixtures.update(
        data.load_lines(ORIGINAL_UNSOLVED.split('\n'), CrypticFixture))
    for fixture in fixtures.values():
      all_clues.append(fixture.clue)
      self.problems[fixture.name] = cryptic_problem.CrypticProblem(
          fixture.name, [fixture.clue])
    # expect(all_clues).to(have_len(51))  # Make fail to see output.
    warehouse.save()
    d = dict([
      (fixture.name.lower(), 100000) for fixture in fixtures.values()
    ])
    d['volcanoes'] = 100000  # For GPH Zero Space.
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

  with it('solves specific examples'):
    with benchmark(1000, stddev=.20):
      solutions = self.problems['MUSIC'].solutions()
      expect(solutions).not_to(be_empty)
      expect(solutions).to(have_key('music'))
      expect(solutions).to(have_key('micro'))
      expect(solutions['music']).to(be_above(solutions['micro']))

      expect(self.problems['HOSTS'].solutions()).not_to(be_empty)
      expect(self.problems['HOSTS'].solutions()).to(have_key('hosts'))

      expect(self.problems['PASTRY'].solutions()).not_to(be_empty)
      expect(self.problems['PASTRY'].solutions()).to(have_key('pastry'))

      expect(self.problems['SASH'].solutions()).not_to(be_empty)
      expect(self.problems['SASH'].solutions()).to(have_key('sash'))

      expect(self.problems['STIGMA'].solutions()).not_to(be_empty)
      expect(self.problems['STIGMA'].solutions()).to(have_key('stigma'))

  with it('solves all problems'):
    with benchmark(4000, stddev=.25):
      incomplete = {
        # Requires synonyms.
        'GREENBELT',
        'MONORAIL',
        # Requires crossword lookups.
        'DUCKS',  # "1+ bird", "lowers head".
        'NINTH',  # "after <this> life".
        'ANGLING',  # Dropping a line.
        'TOAST',  # Here's to you.
        'TWIG',  # Tree shoot, UK "understand".
        'ESCOURT', 'SLING', 'STEAK', 'TWIG',
        # Requires either.
        'DAMAGES', 'RUSHDIE', 'NOTE',
        # ...advanced.
        'SPANNER',  # "Tool for tightening a bridge?".
      }
      incomplete_seen = set()
      unsupported = {
        'PROLONG',  # EMBEDDED indicator but pine == long for some reason.
        'CAPTAINHOOK',  # EMBEDDED indicator but cryptic is 'need of a hand'.
        'FALLINGSTAR',  # EMBEDDED but actually double definition.
        'FLEA',  # HOMOPHONE for "to escape".
      }
      last_resort_matches = {
        'ALCOHOL',  # drink.
        'CRAMPON',  # climber.
        'GAP',  # space.
        'HOSTS',  # entertains.
        'START',  # begin.
      }
      unsupported_seen = set()
      incorrect = {}
      results = {}
      for problem in self.problems:
        try:
          result = dict(self.problems[problem].solutions())
          if result:
            results[problem] = result
          else:
            incomplete_seen.add(problem)
            if problem in incomplete:
              expect(result).to(be_empty)
        except NotImplementedError:
          unsupported_seen.add(problem)
      for problem, value in results.items():
        expect((problem, value)).not_to(equal((problem, {})))
        problem_lower = problem.lower()
        if problem in incorrect:
          expect(value).not_to(have_key(problem_lower))
        else:
          expect(value).to(have_key(problem_lower))
          if problem in last_resort_matches:
            expect(value[problem_lower]).to(be_above(.25))
          else:
            expect(value[problem_lower]).to(equal(1))
      expect(incomplete_seen - incomplete).to(be_empty)
      expect(incomplete - incomplete_seen).to(be_empty)
      expect(unsupported_seen).to(equal(unsupported))
      expect(results).to(have_len(
          len(self.problems) - len(incomplete) - len(unsupported)))
      expect(len(results) / len(self.problems)).to(be_above_or_equal(2 / 3))

  with it('solves a GPH Zero Space puzzle'):
    with benchmark(1000):
      problem = cryptic_problem.CrypticProblem(
          'gphzs', ['Fiery spouts put oven coals in a mess (9)'])
      solutions = problem.solutions()
      expect(solutions).to(have_key('volcanoes'))
      expect(solutions['volcanoes']).to(equal(1))
      expect(solutions.peek()).to(equal('volcanoes'))

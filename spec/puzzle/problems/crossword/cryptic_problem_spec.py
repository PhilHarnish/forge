from data import anagram_index, data, trie, warehouse
from data.word_api import word_api
from puzzle.problems.crossword import cryptic_problem
from spec.mamba import *


class CrypticFixture(object):
  def __init__(self, name, lines):
    self.name = name
    self.clue, self.method = lines[:2]

with description('CrypticCrosswordProblem'):
  with before.all:
    # Sample format of data/cryptic_clues.txt:
    # [AMSTERDAM]
    # Sam dreamt about European port (9)
    # /SAMDREAMPT, {european port}
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
      expect(all_clues).to(have_len(51))  # Make fail to see output.
      warehouse.save()
      d = dict([
        (fixture.name.lower(), 100000) for fixture in self.fixtures.values()
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

    with it('solves gecko'):
      expect(self.problems).to(have_key('GECKO'))
      solutions = self.problems['GECKO'].solutions()
      expect(solutions).not_to(be_empty)
      expect(solutions).to(have_key('gecko'))
      expect(solutions).not_to(have_key('witch'))
      expect(solutions).to(have_key('wight'))
      expect(solutions['gecko']).to(be_above(solutions['wight']))

    with _description('with wordnet'):
      with before.all:
        warehouse.save()
        warehouse.register('/api/words', word_api.get_api('wordnet'))

      with after.all:
        warehouse.restore()

      with it('solves music'):
        solutions = self.problems['MUSIC'].solutions()
        expect(solutions).not_to(be_empty)
        expect(solutions).to(have_key('music'))
        expect(solutions).to(have_key('micro'))
        expect(solutions['music']).to(be_above(solutions['micro']))

      with it('solves hosts'):
        expect(self.problems['HOSTS'].solutions()).not_to(be_empty)
        expect(self.problems['HOSTS'].solutions()).to(have_key('hosts'))

      with it('solves pastry'):
        expect(self.problems['PASTRY'].solutions()).not_to(be_empty)
        expect(self.problems['PASTRY'].solutions()).to(have_key('pastry'))

      with it('solves sash'):
        expect(self.problems['SASH'].solutions()).not_to(be_empty)
        expect(self.problems['SASH'].solutions()).to(have_key('sash'))

      with it('solves all problems'):
        incomplete = {
          # Requires synonyms.
          'GREENBELT',
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
        problem = cryptic_problem.CrypticProblem(
            'gphzs', ['Fiery spouts put oven coals in a mess (9)'])
        solutions = problem.solutions()
        expect(solutions).to(have_key('volcanoes'))
        expect(solutions['volcanoes']).to(equal(1))
        expect(solutions.peek()).to(equal('volcanoes'))

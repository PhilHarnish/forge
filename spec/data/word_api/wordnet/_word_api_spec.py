from data.word_api import word_api
from spec.mamba import *

_word_api = None

with _description('_word_api'):
  with before.all:
    global _word_api
    _word_api = word_api.get_api('wordnet')

  with description('synonyms'):
    with it('executes without error'):
      expect(calling(_word_api.synonyms, 'string')).not_to(raise_error)

    with it('returns synonyms'):
      results = _word_api.synonyms('string')
      expect(results).to(have_keys('fiber', 'cord', 'thread'))

  with description('hypernyms'):
    with it('executes without error'):
      expect(calling(_word_api.hypernyms, 'orange')).not_to(raise_error)

    with it('returns synonyms'):
      results = _word_api.hypernyms('orange')
      expect(results).to(have_keys('pigment', 'color', 'edible fruit'))

  with description('cryptic examples'):
    with it('GREENBELT: Inexperienced band intended to limit urban sprawl'):
      # expect(_word_api.expand('inexperienced')).to(have_key('green'))
      expect(_word_api.expand('band')).to(have_key('belt'))

    with it('PASTRY: Fathers attempt to get pie-crust'):
      expect(_word_api.expand('fathers')).to(have_key('pas'))
      expect(_word_api.expand('attempt')).to(have_key('try'))

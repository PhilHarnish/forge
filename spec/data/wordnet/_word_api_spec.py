from data.wordnet import _word_api
from spec.mamba import *

with description('_word_api'):
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

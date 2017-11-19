from data.word_api import word_api
from spec.mamba import *

_word_api = None

with _description('_word_api'):
  with before.all:
    global _word_api
    _word_api = word_api.get_api('wordnet')

  with description('base_form'):
    with it('handles plurals'):
      expect(_word_api.base_form('snails')).to(equal('snail'))

  with description('expand'):
    with it('expands fiery'):
      expanded = _word_api.expand('fiery')
      expect(expanded).to(have_keys('ardent', 'flaming', 'igneous'))
      expect(expanded).not_to(have_key('fiery'))

  with description('tag'):
    with it('tags empty sentences'):
      expect(_word_api.tag('')).to(equal([]))

    with it('tags real sentence'):
      expect(_word_api.tag(
          'The positions of CEO, analyst, and accountant'
          ' are held by Alex, Sheila, and Sarah.')
      ).to(equal([
        ('The', 'DT'),
        ('positions', 'NNS'),
        ('of', 'IN'),
        ('CEO', 'NNP'),
        (',', ','),
        ('analyst', 'NN'),
        (',', ','),
        ('and', 'CC'),
        ('accountant', 'NN'),
        ('are', 'VBP'),
        ('held', 'VBN'),
        ('by', 'IN'),
        ('Alex', 'NNP'),
        (',', ','),
        ('Sheila', 'NNP'),
        (',', ','),
        ('and', 'CC'),
        ('Sarah', 'NNP'),
        ('.', '.'),
      ]))

  with description('synonyms'):
    with it('executes without error'):
      expect(calling(_word_api.synonyms, 'string')).not_to(raise_error)

    with it('returns synonyms'):
      results = _word_api.synonyms('string')
      expect(results).to(have_keys('fiber', 'cord', 'thread'))

  with description('hypernyms'):
    with it('executes without error'):
      expect(calling(_word_api.hypernyms, 'orange')).not_to(raise_error)

    with it('returns hypernyms'):
      results = _word_api.hypernyms('orange')
      expect(results).to(have_keys('pigment', 'color', 'edible fruit'))

  with description('cryptic examples'):
    with it('GREENBELT: Inexperienced band intended to limit urban sprawl'):
      # expect(_word_api.expand('inexperienced')).to(have_key('green'))
      expect(_word_api.expand('band')).to(have_key('belt'))

    with it('PASTRY: Fathers attempt to get pie-crust'):
      expect(_word_api.expand('fathers')).to(have_key('pas'))
      expect(_word_api.expand('attempt')).to(have_key('try'))

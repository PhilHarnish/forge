from wordnik import WordApi

from data import pickle_cache
from data.wordnik import _client

_API = None


def _get_api():
  global _API
  if not _API:
    _API = WordApi.WordApi(_client.get_client())
  return _API


@pickle_cache.cache('wordnik/synonyms')
def synonyms(word):
  synonyms = set()
  results = _get_api().getRelatedWords(
      word,
      useCanonical=True,
      relationshipTypes=[
        'synonym',
        'hypernym',
        'variant',
        'same-context',
      ],
      limitPerRelationshipType=10,
  )
  for result in results:
    for word in result.words:
      # Remove spaces. E.g. 'string theory' -> 'stringtheory'
      synonyms.add(word.replace(' ', ''))
  return synonyms


@pickle_cache.cache('wordnik/hypernyms')
def hypernyms(word):
  hypernym = set()
  results = _get_api().getRelatedWords(
      word,
      useCanonical=True,
      relationshipTypes=[
        'equivalent',
        'hypernym',
      ],
      limitPerRelationshipType=10,
  )
  for result in results:
    for word in result.words:
      # Remove spaces. E.g. 'string theory' -> 'stringtheory'
      hypernym.add(word.replace(' ', ''))
  return hypernym

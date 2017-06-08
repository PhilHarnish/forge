_DEFAULT_SOURCE = 'wordnet'


def get_api(source):
  if source == 'wordnet':
    from data.word_api.wordnet import _word_api as wordnet_api
    return wordnet_api
  elif source == 'wordnik':
    from data.word_api.wordnik import _word_api as wordnik_api
    return wordnik_api
  raise NotImplementedError('%s word API source not supported' % source)

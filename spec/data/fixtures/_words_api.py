import re

from data import meta

_BASE_FORM = re.compile(r's$', re.IGNORECASE)


def base_form(word: str) -> str:
  return _BASE_FORM.sub('', word)


expand = lambda *args, **kwargs: meta.Meta()
synonyms = lambda *args, **kwargs: meta.Meta()
hypernyms = lambda *args, **kwargs: meta.Meta()

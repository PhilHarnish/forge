import re

_WHITESPACE_RE = re.compile(r'\s*[-_]\s*')
_REMOVE_RE = re.compile(r'(\(\d+\)|[^\w\s])')
_IGNORED = frozenset([
  'a', 'as', 'abbr', 'agcy', 'and',
  'for',
  'eg',
  'gp', 'grp',
  'in', 'it',
  'of', 'on', 'or', 'org',
  'that', 'the', 'to',
])

def _normalize_clue(clue):
  clue = clue.strip()
  clue = re.sub(_WHITESPACE_RE, ' ', clue)
  clue = re.sub(_REMOVE_RE, '', clue)
  return clue


def clue_keywords(clue):
  results = []
  for keyword in _normalize_clue(clue.lower()).split():
    if keyword not in _IGNORED and len(keyword) > 1:
      results.append(keyword)
  return results

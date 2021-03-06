import re
import sqlite3
from typing import Dict, Iterable, List, Tuple

from data import data, warehouse

_WHITESPACE_RE = re.compile(r'\s*[-_,]\s*')
_REMOVE_RE = re.compile(r'(\([\d\s,|]+\)|[^\w\s])')
_IGNORED = frozenset([
  'a', 'as', 'abbr', 'agcy', 'and',
  'for',
  'eg',
  'gp', 'grp',
  'in', 'it',
  'of', 'on', 'or', 'org',
  'that', 'the', 'to',
  'with',
])
_KeywordsType = Dict[str, int]


def _normalize_clue(clue: str) -> str:
  clue = clue.strip()
  clue = re.sub(_WHITESPACE_RE, ' ', clue)
  clue = re.sub(_REMOVE_RE, '', clue)
  return clue


def tokenize_clue(clue: str) -> List[str]:
  return _normalize_clue(clue.lower()).split()


def clue_keywords(clue: str) -> List[str]:
  words_api = warehouse.get('/api/words')
  results = []
  for keyword in tokenize_clue(clue):
    base_form = words_api.base_form(keyword)
    if base_form:
      keyword = base_form
    if keyword not in _IGNORED and len(keyword) > 1:
      results.append(keyword)
  return results


def connect(db: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
  if not db.startswith(':'):
    db = data.project_path(db)
  conn = sqlite3.connect(db)
  return conn, conn.cursor()


def init(db: str) -> sqlite3.Connection:
  conn, cursor = connect(db)
  # Erase previous table.
  cursor.execute('DROP TABLE IF EXISTS clues')
  # Create table.
  cursor.execute("""
    CREATE TABLE clues (
      solution TEXT PRIMARY KEY,
      usages INT,
      keywords TEXT
    )
  """)
  conn.commit()
  return conn


def add(
    cursor: sqlite3.Cursor, solution: str, usages: str,
    keywords: _KeywordsType):
  cmd = 'INSERT INTO clues VALUES (?, ?, ?)'
  try:
    cursor.execute(cmd, (solution, usages, _format_keyword_counts(keywords)))
  except (sqlite3.OperationalError, sqlite3.IntegrityError):
    print(cmd, solution, usages, _format_keywords(keywords))
    raise


def query(cursor: sqlite3.Cursor, clue: str) -> List[Tuple[str, int, _KeywordsType]]:
  results = []
  cmd = """
    SELECT solution, usages, keywords
    FROM clues
    WHERE keywords LIKE ?
  """
  like = '%' + _format_keywords_query(clue_keywords(clue)) + '%'
  for solution, usages, keywords in cursor.execute(cmd, (like,)):
    keywords = _query_keywords(keywords)
    results.append((solution, usages, keywords))
  return results


def _format_keywords(keywords: Iterable[str]):
  return '[%s]' % ']['.join(sorted(keywords))


def _format_keywords_query(keywords: List[str]):
  return '[%s(' % '(%['.join(sorted(keywords))


def _format_keyword_counts(keywords: _KeywordsType) -> str:
  parts = []
  for kvp in keywords.items():
    parts.append('%s(%s)' % kvp)
  return _format_keywords(parts)


def _query_keywords(keywords: str) -> _KeywordsType:
  parts = keywords.strip('][').split('][')
  keywords = {}
  for part in parts:
    k, v = part.rstrip(')').split('(')
    keywords[k] = int(v)
  return keywords

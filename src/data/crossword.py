import re
import sqlite3

_WHITESPACE_RE = re.compile(r'\s*[-_,]\s*')
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


def connect(db):
  conn = sqlite3.connect(db)
  return (conn, conn.cursor())


def init(db):
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


def _format_keywords(keywords):
  return ',[%s],' % '],['.join(sorted(keywords))


def add(cursor, solution, usages, keywords):
  cmd = 'INSERT INTO clues VALUES (?, ?, ?)'
  try:
    cursor.execute(cmd, (solution, usages, _format_keywords(keywords)))
  except (sqlite3.OperationalError, sqlite3.IntegrityError):
    print(cmd, solution, usages, _format_keywords(keywords))
    raise


def query(cursor, clue):
  results = []
  cmd = """
    SELECT solution, usages, keywords
    FROM clues
    WHERE keywords LIKE ?
  """
  like = '%' + _format_keywords(clue_keywords(clue)) + '%'
  for solution, usages, keywords in cursor.execute(cmd, (like,)):
    keywords = clue_keywords(keywords)
    results.append((solution, usages, keywords))
  return results

"""Process http://www.otsys.com/clue/ DB for use with python."""
import collections
import sqlite3

from data import crossword
from data import data

STOP_WORD = '~'  # Appears after z.
MAX_KEYWORDS = 50
MIN_USAGES = 5

VISITED = set()
ALL_SEEN = collections.defaultdict(int)

def _prune_keywords(keywords):
  top = sorted(
      keywords.items(), key=lambda i: i[1], reverse=True
  )[:MAX_KEYWORDS]
  results = {}
  for keyword, count in top:
    ALL_SEEN[keyword] += count
    results[keyword] = count
    if keyword.endswith('s') and len(keyword) > 1:
      # Singularize, just in case. (This won't always produce real words.)
      results[keyword[:-1]] = count
  return results

conn = crossword.init('data/crossword.sqlite')
c = conn.cursor()

def _insert(solution, usages, keywords):
  try:
    crossword.add(c, solution, usages, _prune_keywords(keywords))
  except (sqlite3.OperationalError, sqlite3.IntegrityError):
    conn.commit()
    conn.close()
    raise

last_solution = None
keywords = collections.defaultdict(int)
usages = 0
for i, line in enumerate(
    data.open_project_path('data/clues.txt', errors='ignore')):
  solution, unused_int, unused_year, unused_source, clue = line.lower().split(
      None, 4)
  if solution > STOP_WORD:
    print(line)
    break
  if solution in VISITED:
    print('Skipping %s' % line)
    continue
  if last_solution and solution != last_solution:
    if usages >= MIN_USAGES and keywords:
      _insert(last_solution, usages, keywords)
    VISITED.add(last_solution)
    keywords.clear()
    usages = 0
  usages += 1
  for keyword in crossword.clue_keywords(clue):
    keywords[keyword] += 1
  last_solution = solution

_insert(last_solution, usages, keywords)

conn.commit()
conn.close()

print(_prune_keywords(ALL_SEEN))

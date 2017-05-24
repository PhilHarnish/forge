import itertools
import os

_this_path = os.path.dirname(os.path.realpath(__file__))
_base_path = os.path.join(_this_path.split('/forge/')[0], 'forge')


def _read_lines(project_path):
  abs_path = os.path.join(_base_path, project_path)
  return open(abs_path).read().split('\n')


words = frozenset([
  word for word in _read_lines('data/words.txt') if len(word) in (2, 7)
])

bank = [
  'COLORSOFTHEWIND',
  'DULCINEA',
  'HASADIGAEEBOWAI',
  'JAVERTSSUICIDE',
  'JETSET',
  'LESSONNUMBERONE',
  'OISISUNDOSIRIS',
  'THENIGHTISYOUNGANDYOURESOBEAUTIFUL',
  'WILLPOWER',
  'WONDERFUL',
  'YOUREONLYSECONDRATE',
]

indexes = [3, 3, 1, 7, 8, 13, 1, 8, 2, 1, 4]
visited = set()

counter = 0
for p in itertools.permutations(indexes):
  counter += 1
  if p in visited:
    continue
  visited.add(p)
  constructed = []

  try:
    for i, soln in enumerate(bank):
      constructed.append(soln[p[i] - 1])  # Sub one for 0 based.
    complete = ''.join(constructed)
    w1 = complete[0:2]
    w2 = complete[2:4]
    w3 = complete[4:]
    if counter % 10 or (w1 in words and w2 in words):  # and w3 in words:
      print(p, '=', w1, w2, w3)
  except IndexError:
    pass
  if counter % 5000000 == 0:
    print(p, counter, len(visited))

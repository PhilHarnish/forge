import itertools
from typing import Iterable, List, Optional, Tuple

from data import iter_util

VOWELS = frozenset('aeiouyAEIOUY')
SPECIAL = frozenset('a')  # "a" is a reasonable short word.
ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\'-'
WHITELIST = [chr(code) in ALPHABET for code in range(128)]


def score(word: str, count: int, year: int) -> int:
  if year:
    if year < 1975 or year > 2020:
      return 0
    year_scale = 1 - ((2019 - year) ** 2) / 2056
  else:
    year_scale = 1
  n_vowels = 0
  last_c = ''
  consecutive = 1
  for c in word:
    if ord(c) > 128 or not WHITELIST[ord(c)]:
      return 0
    if c in VOWELS:
      n_vowels += 1
    if c == last_c:
      if consecutive >= 2:
        return 0
      consecutive += 1
    else:
      consecutive = 1
    last_c = c
  if word in SPECIAL:
    word_scale = 1
  elif word[0].isupper():
    if word.isupper():
      word_scale = .5  # All uppercase.
    else:
      word_scale = -.5  # Title case. Counts *against* final score.
  else:
    if word.islower():
      word_scale = 1  # All lowercase.
    else:
      word_scale = .01  # Uppercase somewhere, eg pH.
  # Expect 1+ vowel in every 4 letters.
  vowel_scale = max(.25, min((n_vowels * 4) / len(word), 1))
  return int(count * year_scale * word_scale * vowel_scale)


def aggregate_prefixes(
    iterables: List[Iterable[str]],
    delimiter: str = ' ') -> Iterable[Tuple[str, Optional[list]]]:
  """Aggregate iterables into nested tuples with shared prefixes.

  The iterable streams will be tee'd and consumed like so:
  0 1 2 3 4 ...
  | | | |/|
  | | |/| |
  | |/| | |
  |/| | | |
  x x x x x ...
  """
  n_iterables = len(iterables)
  if n_iterables == 1:
    yield from iter_util.iter_alphabetical_prefixes(
        iterables, delimiter=delimiter)
    return
  carry, iterables[-1] = itertools.tee(iterables[-1])
  for i in reversed(range(1, n_iterables - 1)):
    carry, iterables[i] = itertools.tee(
        iter_util.ensure_prefix(iterables[i], carry, delimiter=delimiter))
  iterables[0] = iter_util.ensure_prefix(
      iterables[0], carry, delimiter=delimiter)
  yield from iter_util.iter_alphabetical_prefixes(
      iterables, delimiter=delimiter)

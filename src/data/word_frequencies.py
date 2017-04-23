"""Library for working with words and word frequencies.

Intended to be used with data from  http://norvig.com/ngrams which is from:
  https://research.googleblog.com/2006/08/all-our-n-gram-are-belong-to-you.html
"""
import functools


from data import data
from data import trie


def load(input):
  return trie.Trie(input)


@functools.lru_cache(1)
def load_from_file(f):
  return load(_parse_file(f))


def _parse_file(f):
  for line in data.open_project_path(f):
    word, weight = line.split()
    yield word, int(weight) or 1

"""Library for working with words and word frequencies.

Intended to be used with data from  http://norvig.com/ngrams which is from:
  https://research.googleblog.com/2006/08/all-our-n-gram-are-belong-to-you.html
"""
import functools

from data import data, trie


def load(input):
  return trie.Trie(input)


@functools.lru_cache(1)
def load_from_file(f):
  return load(parse_file(f))


def parse_file(f):
  for line in data.open_project_path(f):
    parts = line.split()
    weight = parts.pop()
    word = ' '.join(parts)
    yield word, int(weight) or 1

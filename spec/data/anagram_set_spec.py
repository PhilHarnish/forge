from typing import Dict, Set

from data import anagram_set
from spec.mamba import *

with description('anagram_set.from_choices'):
  with it('initializes empty input without error'):
    expect(calling(anagram_set.from_choices, [])).not_to(raise_error)
    expect(anagram_set.from_choices([])).to(be_a(anagram_set.AnagramSet))

  with it('initializes with different iterables'):
    for arg in (['a', 'b'], 'abc', {'a', 'b'}):
      expect(calling(anagram_set.from_choices, arg)).not_to(raise_error)


def lookup(
    source: anagram_set.AnagramSet,
    reference: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
  return {key: set(source[key]) for key in reference}


with description('simple choices'):
  with it('returns input for simple example'):
    subject = anagram_set.from_choices('abc')
    expect(set(subject)).to(equal(set('abc')))

  with it('returns reduced input after slicing'):
    subject = anagram_set.from_choices('abc')
    expected = {
      'a': set('bc'),
      'b': set('ac'),
      'c': set('ab'),
    }
    expect(lookup(subject, expected)).to(equal(expected))

  with it('raises KeyError for invalid access'):
    subject = anagram_set.from_choices('abc')
    bad_inputs = ['aa', 'd', 'abc']
    for input in bad_inputs:
      expect(calling(subject.__getitem__, input)).to(raise_error)

  with it('handles ambiguous input'):
    subject = anagram_set.from_choices(['aab', 'aac', 'a', 'a'])
    expected = {
      'a': set('a'),
      'aa': set('abc'),
      'aab': set('a'),
      'aac': set('a'),
      'aaa': set('abc'),
      'aaab': set('a'),
      'aaaa': set('bc'),
      'aaaab': set('a'),
      'aaaabaa': set('c'),
    }
    expect(lookup(subject, expected)).to(equal(expected))

  with it('caches identical results'):
    subject = anagram_set.from_choices('abc')
    expect(subject['ab']).to(be(subject['ba']))

  with it('compacts clear results'):
    subject = anagram_set.from_choices(['aab', 'a', 'a'])
    expect(repr(subject['aa'])).to(
        equal("AnagramSet(['aab', 'a', 'a'], 'aa')"))
    expect(repr(subject['aab'])).to(
        equal("AnagramSet(['a', 'a'], '')"))

  with it('compacts composable as they become clear'):
    subject = anagram_set.from_choices(['aab', 'a', 'a', 'b'])
    expect(repr(subject['aa'])).to(
        equal("AnagramSet(['aab', 'a', 'a', 'b'], 'aa')"))
    expect(repr(subject['aab'])).to(
        equal("AnagramSet(['aab', 'a', 'a', 'b'], 'aab')"))
    expect(repr(subject['aabb'])).to(
        equal("AnagramSet(['a', 'a'], '')"))
    expect(repr(subject['aaab'])).to(
        equal("AnagramSet(['a', 'b'], '')"))
    expect(subject['aaaba']).to(be(subject['aaaab']))

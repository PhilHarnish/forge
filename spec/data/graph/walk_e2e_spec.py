from typing import List

from data import pickle_cache, word_frequencies
from data.graph import bloom_node, regex, trie, walk
from spec.mamba import *

_FIRST_WORD_WEIGHT = 23135851162
_WORD_LIMIT = 47436  # After "gherkin" which is a cryptic solution in test set.


def get_words(length_mask: int = None, file: str = 'data/count_1w.txt') -> list:
  for word, value in word_frequencies.parse_file(file):
    if value < _WORD_LIMIT:
      break
    elif len(word) > 12:
      continue
    elif not word.isalpha():
      continue
    elif length_mask and (1 << len(word)) & length_mask == 0:
      continue
    last_c = None
    c_chain = 0
    for c in word:
      if c == last_c:
        c_chain += 1
      else:
        last_c = c
        c_chain = 1
      if c_chain >= 3:
        break
    else:
      yield word, value


def make_trie(length_mask) -> bloom_node.BloomNode:
  root = bloom_node.BloomNode()
  for word, value in get_words(length_mask=length_mask):
    trie.add(root, word, value / _FIRST_WORD_WEIGHT)
  return root


@pickle_cache.cache('data/graph/walk_e2e_spec/trie')
def pickled_trie(length_mask: int) -> bloom_node.BloomNode:
  return make_trie(length_mask)


@pickle_cache.cache('data/graph/walk_e2e_spec/unigram_bigram')
def pickled_unigram_bigram(length_mask: int) -> bloom_node.BloomNode:
  unigrams = list(get_words(length_mask=length_mask))
  bigrams = list(get_words(
      length_mask=length_mask, file='data/count_2w_aggregated.txt'))
  root = bloom_node.BloomNode()
  trie.add_ngrams(root, [unigrams, bigrams])
  return root


def results(root) -> List[str]:
  results = []
  for word, _ in walk.walk(root):
    results.append(word)
  return results


def path(root: bloom_node.BloomNode, path: str) -> List[str]:
  result = []
  cursor = root
  for c in path:
    result.append(repr(cursor))
    cursor = cursor[c]
  result.append(repr(cursor))
  return result


def head2head(patterns, trie, words) -> tuple:
  start = time.time()
  merged = trie
  for pattern in patterns:
    merged *= regex.parse(pattern)
  actual = results(merged)
  trie_elapsed = time.time() - start
  start = time.time()
  expressions = [re.compile('^%s$' % pattern) for pattern in patterns]
  expected = [
    word for word, _ in words if all(re.match(exp, word) for exp in expressions)
  ]
  re_elapsed = time.time() - start
  print('trie %.2fx faster for %s' % (re_elapsed / trie_elapsed, patterns))
  return expected, actual


with description('benchmarks: trie creation', 'end2end'):
  with it('creates unigram trie'):
    with benchmark(3500) as should_run:
      if should_run:
        root = make_trie(0b111111110)
        expect(repr(root)).to(equal(
            "BloomNode('abcdefghijklmnopqrstuvwxyz', ' ########', 0)"))

  with it('creates unigram + bigram trie'):
    with benchmark(7000) as should_run:
      if should_run:
        unigrams = list(get_words())
        bigrams = list(get_words(file='data/count_2w_aggregated.txt'))
        root = bloom_node.BloomNode()
        trie.add_ngrams(root, [unigrams, bigrams])
        expect(path(root, 'to be a')).to(equal([
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', ' ############', 0)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', '############', 0.0006713145844190183)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', '###########', 0.02097509031643418)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', ' ############', 0)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', '############', 2.9005393996133883e-05)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', '###########', 0.0001657494654788442)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', ' ############', 0.0)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', '############', 2.5089529173969956e-05)"
        ]))

with description('benchmarks: node merging', 'end2end') as self:
  with before.all:
    self.root = pickled_trie(1 << 7)
    self.words = list(get_words())

  with it('finds nodes matching .e.k.n.'):
    expected, actual = head2head(['.e.k.n.'], self.root, self.words)
    expect(actual).to(equal(expected))

  with it('finds nodes matching s.e.i.g'):
    expected, actual = head2head(['s.e.i.g'], self.root, self.words)
    expect(actual).to(equal(expected))

  with it('finds nodes matching multiple regular expressions'):
    expected, actual = head2head(['s.e.i.g', '.e.k.n.'], self.root, self.words)
    expect(actual).to(equal(expected))
    expect(actual).to(equal(['seeking']))

  with it('finds nodes for very expensive queries'):
    expected, actual = head2head([
      '...alls',
    ], self.root, self.words)
    expect(actual).to(equal(expected))
    expect(actual).to(equal([
      'recalls', 'ingalls', 'adcalls', 'befalls', 'thralls', 'squalls',
      'mccalls'
    ]))

  with it('finds nodes for very expensive queries'):
    expected, actual = head2head([
      '.......',
      '...a...',
      '....l..',
      '.....l.',
      '......s',
    ], self.root, self.words)
    expect(expected).to(equal(actual))
    expect(actual).to(equal([
      'recalls', 'ingalls', 'adcalls', 'befalls', 'thralls', 'squalls',
      'mccalls'
    ]))

with description('benchmarks: unigram/bigram walk', 'end2end') as self:
  with before.all:
    self.root = pickled_unigram_bigram(0b111111)

  with it('should find common results'):
    words = []
    for word, _ in walk.walk(self.root):
      words.append(word)
      if len(words) > 10:
        break
    #words = [word for _, word in zip(range(10), walk.walk(self.root))]
    expect(words).to(equal([
      'the', 'of', 'and', 'to', 'a', 'in', 'for', 'is', 'on', 'that', 'by',
    ]))

  with it('should find explicit solutions'):
    merged = self.root * regex.parse('plums of wrath')
    expect(results(merged)).to(equal(['plums of wrath']))

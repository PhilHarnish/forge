from typing import List

from data import pickle_cache, word_frequencies
from data.graph import bloom_node, regex, trie, walk
from spec.mamba import *

_FIRST_WORD_WEIGHT = 23135851162
_WORD_LIMIT = 47436  # After "gherkin" which is a cryptic solution in test set.


def get_words() -> list:
  for word, value in word_frequencies.parse_file('data/count_1w.txt'):
    if value < _WORD_LIMIT:
      break
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
  for word, value in get_words():
    if 2 ** len(word) & length_mask == 0:
      continue
    trie.add(root, word, value / _FIRST_WORD_WEIGHT)
  return root


@pickle_cache.cache('data/graph/walk_e2e_spec/trie')
def pickled_trie(length_mask: int) -> bloom_node.BloomNode:
  return make_trie(length_mask)


def results(root) -> List[str]:
  results = []
  for word, _ in walk.walk(root):
    results.append(word)
  return results


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
  with it('runs'):
    with benchmark(3500) as should_run:
      if should_run:
        root = make_trie(0b111111110)
        expect(repr(root)).to(equal(
            "BloomNode('abcdefghijklmnopqrstuvwxyz', ' ########', 0)"))


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

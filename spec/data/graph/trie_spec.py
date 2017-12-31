from typing import List

from data.graph import bloom_node, regex, trie
from spec.mamba import *


def _scale(items: list) -> list:
  scale = items[0][1]
  return [(k, v / scale) for k, v in items]


_TEST_DATA = _scale([
    ('the', 23135851162),
    ('of', 13151942776),
    ('and', 12997637966),
    ('to', 12136980858),
    ('a', 9081174698),
    ('in', 8469404971),
    ('for', 5933321709),
    ('is', 4705743816),
    ('on', 3750423199),
    ('that', 3400031103),
])


def path(root: bloom_node.BloomNode, path: str) -> List[str]:
  result = []
  cursor = root
  for c in path:
    result.append(repr(cursor))
    cursor = cursor[c]
  result.append(repr(cursor))
  return result


with description('add'):
  with it('executes without error'):
    root = bloom_node.BloomNode()
    expect(calling(trie.add, root, 'key', 1.0)).not_to(raise_error)

  with it('accumulates data'):
    root = bloom_node.BloomNode()
    trie.add(root, 'key', 1.0)
    expect(root).to(have_len(1))
    trie.add(root, 'another', 1.0)
    expect(root).to(have_len(2))

  with it('maintains bloom properties'):
    root = bloom_node.BloomNode()
    trie.add(root, 'bad', 1.0)
    trie.add(root, 'bag', .50)
    trie.add(root, 'ban', .25)
    expect(repr(root)).to(equal("BloomNode('ABdgn', '   #', 0)"))
    expect(root).to(have_len(1))
    expect(repr(root['b'])).to(equal("BloomNode('Adgn', '  #', 0)"))
    expect(root['b']).to(have_len(1))
    expect(repr(root['b']['a'])).to(equal("BloomNode('dgn', ' #', 0)"))
    expect(root['b']['a']).to(have_len(3))

  with it('maintains bloom properties for longer word + substring'):
    node = bloom_node.BloomNode()
    trie.add(node, 'com', 0.5)
    trie.add(node, 'common', 1.0)
    expect(path(node, 'common')).to(equal([
      # START.
      "BloomNode('CMnO', '   #  #', 0)",
      # -> c.
      "BloomNode('MnO', '  #  #', 0)",
      # -> o.
      "BloomNode('Mno', ' #  #', 0)",
      # -> m.
      "BloomNode('MNO', '#  #', 0.5)",
      # -> m.
      "BloomNode('NO', '  #', 0)",
      # -> o.
      "BloomNode('N', ' #', 0)",
      # -> n.
      "BloomNode('', '#', 1.0)",
    ]))


with description('merge'):
  with it('merges to zero results for unrelated tries'):
    a = bloom_node.BloomNode()
    trie.add(a, 'abc', 1.0)
    b = bloom_node.BloomNode()
    trie.add(b, 'xyz', 1.0)
    merged = a * b
    expect(merged).to(have_len(0))

  with it('predicts non-overlap for suffixes'):
    a = bloom_node.BloomNode()
    trie.add(a, 'cab', 1.0)
    b = bloom_node.BloomNode()
    trie.add(b, 'cat', 1.0)
    merged = a * b
    expect(merged).to(have_len(0))

  with it('predicts overlap for identical tries'):
    a = bloom_node.BloomNode()
    trie.add(a, 'cat', 1.0)
    b = bloom_node.BloomNode()
    trie.add(b, 'cat', 1.0)
    merged = a * b
    expect(merged).to(have_len(1))


with description('test data, 1 word'):
  with before.each:
    self.trie = bloom_node.BloomNode()
    for key, value in _TEST_DATA:
      trie.add(self.trie, key, value)

  with it('populates test data'):
    expect(repr(self.trie)).to(equal("BloomNode('adefhinorst', ' ####', 0)"))

  with it('should consider some merges impossible'):
    expression = regex.parse('.n')
    child1 = self.trie['t']
    child2 = expression['t']
    expect(child1 * child2).to(have_len(0))

  with it('merges with regex'):
    expression = regex.parse('.n')
    merged = self.trie * expression
    expect(repr(merged)).to(equal("BloomNode('iNo', '  #', 0)"))
    expect(repr(merged['i'])).to(equal("BloomNode('N', ' #', 0)"))


with description('test data, multiple word'):
  with before.each:
    self.trie = bloom_node.BloomNode()
    for key, value in _TEST_DATA:
      trie.add(self.trie, key, value)
    for key, value in _TEST_DATA:
      trie.add_multi_word(self.trie, key, value)

  with it('populates test data'):
    expect(repr(self.trie)).to(equal("BloomNode('adefhinorst; ', ' ####', 0)"))

  with it('should allow looping back to root'):
    expect(repr(self.trie['i']['s'][' '])).to(equal(
        "BloomNode('adefhinorst; ', ' ####', 0)"))

  with it('should weigh later word matches less than original'):
    expect(self.trie['i']['s'].match_weight).to(be_above(
        self.trie['i']['s'][' ']['i']['s'].match_weight))

  with it('should weigh even later word matches less than later'):
    expect(self.trie['i']['s'][' ']['i']['s'].match_weight).to(be_above(
        self.trie['i']['s'][' ']['i']['s'][' ']['i']['s'].match_weight))

  with it('should repr correctly in deep test'):
    expect(path(self.trie, 'is is is')).to(equal([
      # START.
      "BloomNode('adefhinorst; ', ' ####', 0)",
      # -> i.
      "BloomNode('ns; ', ' #', 0)",
      # -> s.
      "BloomNode(' ', '#', 0.20339618296512277)",
      # ->  .
      "BloomNode('adefhinorst; ', ' ####', 0)",
      # -> i.
      "BloomNode('ns; ', ' #', 0.0)",
      # -> s.
      "BloomNode(' ', '#', 0.041370007244781695)",
      # ->  .
      "BloomNode('adefhinorst; ', ' ####', 0.0)",
      # -> i.
      "BloomNode('ns; ', ' #', 0.0)",
      # -> s.
      "BloomNode(' ', '#', 0.008414501562828072)",
    ]))


with description('add_ngrams'):
  with before.all:
    self.unigrams = [
      ('a', 50),
      ('ab', 25),
      ('abc', 15),
      ('abcd', 10),
    ]
    self.bigrams = [
      ('a a', 25),
      ('a ab', 15),
      ('a abc', 10),
      ('ab ab', 10),
      ('ab abc', 10),
      ('ab abcd', 5),
      ('abc abc', 10),
      ('abc abcd', 5),
      ('abcd abcd', 10),
    ]

  with it('ignores empty input'):
    root = bloom_node.BloomNode()
    trie.add_ngrams(root, [])
    expect(root).to(have_len(0))

  with it('adds unigrams'):
    root = bloom_node.BloomNode()
    trie.add_ngrams(root, [self.unigrams])
    expect(repr(root)).to(equal("BloomNode('Abcd; ', ' ####', 0)"))

  with it('buckets into percentiles'):
    root = bloom_node.BloomNode()
    unigrams = [
      (c, i + 1) for c, i in zip('abcdefghij', range(26))
    ]
    trie.add_ngrams(root, [unigrams], n_percentiles=4)
    expect(repr(root)).to(equal("BloomNode('abcdefghij; ', ' #', 0)"))
    expect([
      '%s: %s' % (c, root[c][' '].op) for c in 'abcdefghij'
    ]).to(equal([
      "a: (BloomNode('abcdefghij; ', ' #', 0)*0.01818181818181818)",
      "b: (BloomNode('abcdefghij; ', ' #', 0)*0.01818181818181818)",
      "c: (BloomNode('abcdefghij; ', ' #', 0)*0.01818181818181818)",
      "d: (BloomNode('abcdefghij; ', ' #', 0)*0.07272727272727272)",
      "e: (BloomNode('abcdefghij; ', ' #', 0)*0.07272727272727272)",
      "f: (BloomNode('abcdefghij; ', ' #', 0)*0.10909090909090909)",
      "g: (BloomNode('abcdefghij; ', ' #', 0)*0.10909090909090909)",
      "h: (BloomNode('abcdefghij; ', ' #', 0)*0.10909090909090909)",
      "i: (BloomNode('abcdefghij; ', ' #', 0)*0.16363636363636364)",
      "j: (BloomNode('abcdefghij; ', ' #', 0)*0.16363636363636364)"
    ]))

  with it('adds unigrams and bigrams'):
    root = bloom_node.BloomNode()
    trie.add_ngrams(root, [self.unigrams, self.bigrams])
    expect(repr(root)).to(equal("BloomNode('Abcd; ', ' ####', 0)"))

  with description('unigrams and bigrams'):
    with before.each:
      self.trie = bloom_node.BloomNode()
      trie.add_ngrams(self.trie, [self.unigrams, self.bigrams])

    with it('expands unigrams'):
      expect(path(self.trie, 'a')).to(equal([
        "BloomNode('Abcd; ', ' ####', 0)",
        "BloomNode('Bcd; ', '####', 0.5)",
      ]))

    with it('expands specified bigrams'):
      expect(path(self.trie, 'a ab')).to(equal([
        "BloomNode('Abcd; ', ' ####', 0)",
        "BloomNode('Bcd; ', '####', 0.5)",  # c(a)/total = 50/100.
        "BloomNode('Abcd; ', ' ####', 0)",
        "BloomNode('Bcd; ', '####', 0.5)",  # c(a a)/c(a) = 25 / 50.
        "BloomNode('Cd; ', '###', 0.3)",  # c(a ab)/c(a) = 15 / 50.
      ]))

    with it('expands invented bigrams'):
      expect(path(self.trie, 'ab a')).to(equal([
        "BloomNode('Abcd; ', ' ####', 0)",
        "BloomNode('Bcd; ', '####', 0.5)",  # c(a)/total = 50/100.
        "BloomNode('Cd; ', '###', 0.25)",  # c(ab)/total = 25/100.
        "BloomNode('Abcd; ', ' ####', 0)",
        # P(ab a) = P(ab *)*P(a) = c(ab a)/c(ab)*P(a) = min(ab *)/c(ab)*P(a) =
        # 5/25 * .5 = .1.
        "BloomNode('Bcd; ', '####', 0.1)",
      ]))

    with it('expands invented familiar trigrams'):
      expect(path(self.trie, 'a a a')).to(equal([
        "BloomNode('Abcd; ', ' ####', 0)",
        "BloomNode('Bcd; ', '####', 0.5)",  # c(a)/total = 50/100.
        "BloomNode('Abcd; ', ' ####', 0)",
        "BloomNode('Bcd; ', '####', 0.5)",  # c(a a)/c(a) = 25/50.
        "BloomNode('Abcd; ', ' ####', 0.0)",
        "BloomNode('Bcd; ', '####', 0.25)",  # c(a a)/c(a) * P(a) = 25/50 * .5.
      ]))

    with it('expands invented unusual trigrams'):
      node = self.trie['a']
      node = node['b']
      node = node[' ']
      node = node['a']
      node = node[' ']
      node = node['a']
      expect(path(self.trie, 'ab a a')).to(equal([
        "BloomNode('Abcd; ', ' ####', 0)",
        "BloomNode('Bcd; ', '####', 0.5)",  # c(a)/total = 50/100.
        "BloomNode('Cd; ', '###', 0.25)",  # c(ab)/total = 25/100.
        "BloomNode('Abcd; ', ' ####', 0)",
        "BloomNode('Bcd; ', '####', 0.1)",
        "BloomNode('Abcd; ', ' ####', 0.0)",
        "BloomNode('Bcd; ', '####', 0.1)",
      ]))

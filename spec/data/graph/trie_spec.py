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
    expecteds = [
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
    ]
    for c, expected in zip('common', expecteds):
      expect(str(node)).to(equal(expected))
      node = node[c]
    expect(repr(node)).to(equal(expecteds[-1]))


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
    expecteds = [
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
    ]
    node = self.trie
    for c, expected in zip('is is is', expecteds):
      node = node[c]
      expect(str(repr(node))).to(equal(expected))

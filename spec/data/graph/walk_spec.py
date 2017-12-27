from data.graph import bloom_node, regex, trie, walk
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

with description('test data'):
  with before.each:
    self.test_data = bloom_node.BloomNode()
    for k, v in _TEST_DATA:
      trie.add(self.test_data, k, v)

  with it('walks all items, in order'):
    for expected, actual in zip(_TEST_DATA, walk.walk(self.test_data)):
      expected_word, expected_weight = expected
      actual_word, actual_weight = actual
      expect(expected_word).to(equal(actual_word))
      expect(actual_weight).to(equal(expected_weight))

  with it('finds regex matches'):
    expression = regex.parse('.n')
    merged = self.test_data * expression
    expect(list(walk.walk(merged))).to(equal([
      ('in', 0.3660727635087299),
      ('on', 0.16210439688339484)
    ]))

from data.seek import base_seek, node, walker
from spec.mamba import *

_TEST_DATA = [
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
]

with description('test data'):
  with before.each:
    n = node.Node()
    for k, v in _TEST_DATA:
      n.add(k, v)
    s = base_seek.BaseSeek(n)
    self.subject = walker.Walker(s)

  with it('walks all items, in order, between [0, 1]'):
    last_weight = 1
    for expected, actual in zip(_TEST_DATA, self.subject):
      expected_word, _ = expected
      actual_word, actual_weight = actual
      expect(expected_word).to(equal(actual_word))
      expect(actual_weight).to(be_below_or_equal(last_weight))
      last_weight = actual_weight
    expect(last_weight).to(be_above_or_equal(0))

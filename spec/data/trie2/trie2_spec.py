from data.trie2 import trie2
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

with description('trie2'):
  with description('test data'):
    with before.each:
      self.subject = trie2.Trie2(_TEST_DATA)

    with it('instantiates'):
      expect(self.subject).to(have_len(len(_TEST_DATA)))

    with it('has recall'):
      last_weight = float('inf')
      for key, weight in _TEST_DATA:
        expect(key in self.subject).to(be_true)
        expect(self.subject[key]).to(be_below_or_equal(1))
        expect(self.subject[key]).to(be_below(last_weight))
        last_weight = weight

  with it('preserves weights already <= 1'):
    t = trie2.Trie2((
        ('a', 1),
        ('aa', 0.9),
    ))
    expect(t['a']).to(equal(1))
    expect(t['aa']).to(equal(0.9))
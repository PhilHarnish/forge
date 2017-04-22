from expects import *

from src.data import trie
from spec.data.fixtures import tries

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

with description('trie'):
  with it('instantiates'):
    t = trie.Trie(_TEST_DATA)
    expect(t).to(have_len(len(_TEST_DATA)))

  with it('has recall'):
    t = trie.Trie(_TEST_DATA)
    for key, weight in _TEST_DATA:
      expect(key in t).to(be_true)
      expect(t[key]).to(equal(weight))

  with context('letters'):
    with it('should match every letter'):
      t = tries.letters()
      for c in 'abcdefghijklmnopqrstuvwxyz':
        expect(c in t).to(be_true)

    with it('should weight a > i > all other letters'):
      t = tries.letters()
      a = t['a']
      i = t['i']
      expect(a).to(be_above(i))
      for c in 'bcdefghjklmnopqrstuvwxyz':
        expect(t[c]).to(be_below(a))
        expect(t[c]).to(be_below(i))

  with context('ambiguous sentences'):
    with it('should include letters'):
      t = tries.ambiguous()
      for c in 'abcdefghijklmnopqrstuvwxyz':
        expect(c in t).to(be_true)

    with it('should prefix match ambiguous prefixes'):
      # superbowlwarplanefireshipsnapshotscrapbookisnowhere
      t = tries.ambiguous()
      expect(set(t.keys('super'))).to(contain(
          'super', 'superb', 'superbowl'))
      expect(set(t.keys('war'))).to(contain(
          'warplane', 'warplanes', 'war', 'warp'))
      expect(set(t.keys('snap'))).to(contain(
          'snaps', 'snapshots', 'snap', 'snapshot'))

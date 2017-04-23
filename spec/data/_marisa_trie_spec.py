from spec.mamba import *
from spec.data.fixtures import tries
from src.data import _marisa_trie

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
  with context('test data'):
    with before.each:
      self.subject = _marisa_trie.Trie(_TEST_DATA)

    with it('instantiates'):
      expect(self.subject).to(have_len(len(_TEST_DATA)))

    with it('has recall'):
      for key, weight in _TEST_DATA:
        expect(key in self.subject).to(be_true)
        expect(self.subject[key]).to(equal(weight))

  with context('letters'):
    with before.each:
      self.subject = _marisa_trie.Trie(tries.letters().items())

    with it('should match every letter'):
      for c in 'abcdefghijklmnopqrstuvwxyz':
        expect(c in self.subject).to(be_true)

    with it('should weight a > i > all other letters'):
      a = self.subject['a']
      i = self.subject['i']
      expect(a).to(be_above(i))
      for c in 'bcdefghjklmnopqrstuvwxyz':
        expect(self.subject[c]).to(be_below(a))
        expect(self.subject[c]).to(be_below(i))

  with context('ambiguous sentences'):
    with before.each:
      self.subject = _marisa_trie.Trie(tries.ambiguous().items())

    with it('should include letters'):
      for c in 'abcdefghijklmnopqrstuvwxyz':
        expect(c in self.subject).to(be_true)

    with it('should prefix match ambiguous prefixes'):
      # superbowlwarplanefireshipsnapshotscrapbookisnowhere
      expect(set(self.subject.keys('super'))).to(contain(
          'super', 'superb', 'superbowl'))
      expect(set(self.subject.keys('war'))).to(contain(
          'warplane', 'warplanes', 'war', 'warp'))
      expect(set(self.subject.keys('snap'))).to(contain(
          'snaps', 'snapshots', 'snap', 'snapshot'))

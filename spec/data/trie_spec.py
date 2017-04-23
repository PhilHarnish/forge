from spec.data.fixtures import tries
from spec.mamba import *
from src.data import trie


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
      self.subject = trie.Trie(_TEST_DATA)

    with it('instantiates'):
      expect(self.subject).to(have_len(len(_TEST_DATA)))

    with it('has recall'):
      for key, weight in _TEST_DATA:
        expect(key in self.subject).to(be_true)
        expect(self.subject[key]).to(equal(weight))

    with description('items'):
      with it('all results'):
        expect(self.subject.items()).to(have_len(len(_TEST_DATA)))

      with it('prefix results'):
        expect(self.subject.items('th')).to(equal([
          ('the', 23135851162), ('that', 3400031103)
        ]))

      with it('prefix + seek results'):
        expect(self.subject.items('t', 'ho')).to(equal([
          ('the', 23135851162), ('to', 12136980858), ('that', 3400031103)
        ]))

  with context('letters'):
    with before.each:
      self.subject = tries.letters()

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
      self.subject = tries.ambiguous()

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

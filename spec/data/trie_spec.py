import pickle
import statistics

from data import trie
from data.seek_sets import seek_set
from spec.data.fixtures import tries
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

    with it('reports max value'):
      expect(self.subject.magnitude()).to(equal(max(i[1] for i in _TEST_DATA)))

    with it('reports interesting threshold'):
      expect(self.subject.interesting_threshold()).to(be_between(
          statistics.median(i[1] for i in _TEST_DATA),
          _TEST_DATA[0][1]
      ))

    with description('items'):
      with it('all results'):
        expect(self.subject).to(have_len(len(_TEST_DATA)))

    with description('has_keys_with_prefix'):
      with before.each:
        self.subject = tries.ambiguous()

      with it('rejects garbage prefixes'):
        expect(self.subject.has_keys_with_prefix('fsdfasa')).to(be_false)

      with it('matches valid prefixes'):
        expect(call(self.subject.has_keys_with_prefix, 'super')).to(equal(True))
        expect(call(self.subject.has_keys_with_prefix, 'superb')).to(
            equal(True))
        expect(call(self.subject.has_keys_with_prefix, 'superbowl')).to(
            equal(True))

    with description('walk'):
      with it('returns nothing for garbage input'):
        expect(self.subject.walk(['@'])).to(be_empty)

      with it('returns 1 letter results when given matching letter'):
        expect(list(self.subject.walk(['a']))).to(equal([('a', 9081174698)]))

      with it('returns 1 and 2 letter results when given alphabet x2'):
        expect(list(self.subject.walk(
            ['abcdefghijklmnopqrstuvwxyz'] * 2,
            exact_match=False,
        ))).to(equal([
          ('of', 13151942776), ('to', 12136980858),
          ('a', 9081174698),
          ('in', 8469404971), ('is', 4705743816), ('on', 3750423199)
        ]))

      with it('returns only 2 letter results when exact_match is required'):
        expect(list(self.subject.walk(
            ['abcdefghijklmnopqrstuvwxyz'] * 2,
            exact_match=True,
        ))).to(equal([
          ('of', 13151942776), ('to', 12136980858),
          ('in', 8469404971), ('is', 4705743816), ('on', 3750423199)
        ]))

      with it('returns specific matches when given constraints'):
        expect(list(self.subject.walk([
          set('answer'),
          set('anything'),
          set('matched'),
        ]))).to(equal([('and', 12997637966), ('a', 9081174698)]))

      with description('using SeekSet'):
        with it('works with old functionality'):
          sets = seek_set.SeekSet(['abcdefghijklmnopqrstuvwxyz'] * 2)
          expect(list(self.subject.walk(sets, exact_match=False))).to(equal([
            ('of', 13151942776), ('to', 12136980858),
            ('a', 9081174698),
            ('in', 8469404971), ('is', 4705743816), ('on', 3750423199)
          ]))

        with it('works with permutations'):
          sets = seek_set.SeekSet(['ns', 'i'], sets_permutable=True)
          expect(list(self.subject.walk(sets))).to(equal([
            ('in', 8469404971), ('is', 4705743816)
          ]))

        with it('works with indexes'):
          sets = seek_set.SeekSet(
              ['txxx', 'xhxx', 'xxax', 'xxxt'],
              indexes=[1, 2, 3, 4]
          )
          expect(list(self.subject.walk(sets))).to(equal([
            ('that', 3400031103)
          ]))

        with it('works with permutable sets and fixed indexes'):
          sets = seek_set.SeekSet(
              ['xxax', 'xxxt', 'txxx', 'xhxx'],
              indexes=[1, 2, 3, 4],
              sets_permutable=True,
          )
          expect(list(self.subject.walk(sets))).to(equal([
            ('that', 3400031103)
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

  with description('pickling'):
    with it('should be possible to pickle Trie'):
      t = tries.letters()
      expect(calling(pickle.dumps, t)).not_to(raise_error)

    with it('should be possible to recreat Trie from pkl'):
      t = tries.letters()
      b = pickle.dumps(t)
      expect(b).not_to(be_empty)
      t2 = pickle.loads(b)
      expect(t2).to(be_a(trie.Trie))
      expect(t2).to(have_len(len(t)))

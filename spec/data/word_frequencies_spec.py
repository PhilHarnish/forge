import textwrap

from expects import *
from mock import patch

from src.data import word_frequencies
from spec.data.fixtures import tries

patcher = patch.object(word_frequencies.data, 'open_project_path')
_SMALL_FILE = textwrap.dedent("""
    the	23135851162
    of	13151942776
    and	12997637966
    to	12136980858
    a	9081174698
    in	8469404971
    for	5933321709
    is	4705743816
    on	3750423199
    that	3400031103
""").strip()

with description('word_frequencies'):
  with before.all:
    mock = patcher.start()
    mock.return_value = _SMALL_FILE.split('\n')

  with after.all:
    patcher.stop()

  with it('loads'):
    expect(word_frequencies.load_from_file('test')).to(have_len(10))

  with it('should have results'):
    t = word_frequencies.load_from_file('test')
    results = []
    for key, value in t.iteritems():
      results.append([key, int.from_bytes(value, 'little')])
    expect(results).to(equal([
      # th...
      ['the', 23135851162],
      ['that', 3400031103],
      # to...
      ['to', 12136980858],
      # a...
      ['and', 12997637966],
      ['a', 9081174698],
      # o...
      ['of',  13151942776],
      ['on',   3750423199],
      # i...
      ['in',   8469404971],
      ['is',   4705743816],
      # f...
      ['for',  5933321709],
    ]))

  with context('letters'):
    with it('should match every letter'):
      trie = tries.letters()
      for c in 'abcdefghijklmnopqrstuvwxyz':
        expect(c in trie).to(be_true)

    with it('should weight a > i > all other letters'):
      trie = tries.letters()
      a = trie['a']
      i = trie['i']
      expect(a).to(be_above(i))
      for c in 'bcdefghjklmnopqrstuvwxyz':
        expect(trie[c]).to(be_below(a))
        expect(trie[c]).to(be_below(i))

  with context('ambiguous sentences'):
    with it('should include letters'):
      trie = tries.ambiguous()
      for c in 'abcdefghijklmnopqrstuvwxyz':
        expect(c in trie).to(be_true)

    with it('should prefix match ambiguous prefixes'):
      # superbowlwarplanefireshipsnapshotscrapbookisnowhere
      trie = tries.ambiguous()
      expect(set(trie.keys('super'))).to(contain(
          'super', 'superb', 'superbowl'))
      expect(set(trie.keys('war'))).to(contain(
          'warplane', 'warplanes', 'war', 'warp'))
      expect(set(trie.keys('snap'))).to(contain(
          'snaps', 'snapshots', 'snap', 'snapshot'))

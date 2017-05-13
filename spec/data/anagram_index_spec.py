from data import anagram_index
from spec.data.fixtures import tries
from spec.mamba import *

with description('anagram_index'):
  with before.all:
    self.subject = anagram_index.AnagramIndex(tries.ambiguous())

  with it('instantiates'):
    expect(len(self.subject)).to(be_above(0))

  with it('accepts pre-sort-jumbled anagrams'):
    expect(self.subject).to(have_key('low'))

  with it('accepts anti-sort-jumbled anagrams'):
    expect(self.subject).to(have_key('wlo'))

  with it('returns multiple matches'):
    expect(self.subject['snap']).to(equal(['snap', 'naps']))

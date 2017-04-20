import textwrap
import timeit

from expects import *
from mock import patch

from src.data import word_frequencies

patcher = patch.object(word_frequencies.data, 'open_project_path')

with description('word_frequencies'):
  with before.all:
    mock = patcher.start()
    mock.return_value = textwrap.dedent("""
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
    """).strip().split('\n')

  with after.all:
    patcher.stop()

  with it('loads'):
    expect(word_frequencies.trie()).to(have_len(10))

  with it('should have results'):
    t = word_frequencies.trie()
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

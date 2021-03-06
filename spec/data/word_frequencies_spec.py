from mock import patch

from data import word_frequencies
from spec.mamba import *

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
    multiple words 1000000000
""").strip()

with description('word_frequencies'):
  with before.all:
    mock = patcher.start()
    mock.return_value = _SMALL_FILE.split('\n')

  with after.all:
    patcher.stop()

  with it('loads'):
    expect(word_frequencies.load_from_file('test')).to(have_len(11))

  with it('memoizes one file result'):
    with patch.object(word_frequencies, 'load') as mock_load:
      expect(mock_load.call_count).to(equal(0))
      word_frequencies.load_from_file('example1')
      expect(mock_load.call_count).to(equal(1))
      word_frequencies.load_from_file('example1')
      expect(mock_load.call_count).to(equal(1))
      word_frequencies.load_from_file('example2')
      expect(mock_load.call_count).to(equal(2))

  with it('should have results'):
    t = word_frequencies.load_from_file('test')
    expect(list(t.walk(
        ['abcdefghijklmnopqrstuvwxyz'] * 4,
        exact_match=False)
    )).to(equal([
      ('the', 23135851162),
      ('of', 13151942776),
      ('and', 12997637966),
      ('to', 12136980858),
      ('a', 9081174698),
      ('in', 8469404971),
      ('for', 5933321709),
      ('is', 4705743816),
      ('on', 3750423199),
      ('that', 3400031103)
    ]))

  with it('should should store multi-word results'):
    t = word_frequencies.load_from_file('test')
    expect(t).to(have_key('multiple words'))

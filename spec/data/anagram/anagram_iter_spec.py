from data.anagram import anagram_iter
from spec.mamba import *


with description('anagram_iter.from_choices'):
  with it('initializes empty input without error'):
    expect(calling(anagram_iter.from_choices, [])).not_to(
        raise_error)
    expect(anagram_iter.from_choices([])).to(
        be_a(anagram_iter.AnagramIter))

  with it('initializes with different iterables'):
    cases = (
        # Primitives.
        ['a', 'a', 'a'],
        ['a', 'b', 'c'],
        [1, 2, 3],
        'iterable',
        # Functions.
        [abs, id, int],  # Returns int.
        [ascii, str, repr],  # Returns str.
        [id, id, id],  # Duplicates.
    )
    for arg in cases:
      expect(calling(anagram_iter.from_choices, arg)).not_to(raise_error)


with description('simple iterative usage'):
  with it('iterates 1 result for 1 input'):
    ats = anagram_iter.from_choices([13])
    expect(list(ats)).to(equal([13]))

  with it('lists items for 1 input'):
    ats = anagram_iter.from_choices([13])
    expect(list(ats.items())).to(equal([(13, ats[13])]))

  with it('raises for invalid requests'):
    expect(lambda: anagram_iter.from_choices([13])[11]).to(
        raise_error(KeyError, 11))

  with it('exhausts input'):
    ats = anagram_iter.from_choices([13])
    expect(list(ats[13].items())).to(equal([]))
    expect(lambda: ats[13][13]).to(raise_error(KeyError, 13))

  with it('lists options for 2 unique inputs'):
    ats = anagram_iter.from_choices([13, 17])
    expect(list(ats.items())).to(equal([
      (13, ats[13]),
      (17, ats[17]),
    ]))

  with it('lists one option for 2 duplicate inputs'):
    ats = anagram_iter.from_choices([13, 13])
    expect(list(ats.items())).to(equal([
      (13, ats[13]),
    ]))

  with it('duplicate items are both available'):
    ats = anagram_iter.from_choices([13, 13])
    expect(list(ats[13].items())).to(equal([(13, ats[13][13])]))

  with it('duplicate items are exhaustable'):
    expect(calling(lambda: anagram_iter.from_choices([13, 13])[13][13][13])).to(
        raise_error(KeyError, 13))

  with it('produces a list of the final choices'):
    ats = anagram_iter.from_choices([13, 13, 15])
    expect(list(ats.final_choices())).to(equal([
      (13, ats[15][13]),
      (15, ats[13][13]),
    ]))


with description('complex iterative usage'):
  with it('merges paths with common suffix'):
    ats = anagram_iter.from_choices('abc')
    expect(ats['a']['b']).to(equal(ats['b']['a']))

  with it('merges paths with duplicates'):
    ats = anagram_iter.from_choices('abcaa')
    expect(ats['a']['b']).to(equal(ats['b']['a']))

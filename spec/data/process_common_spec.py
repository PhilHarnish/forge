from data import process_common
from spec.mamba import *


with description('score'):
  with it('scores 0 for bad years'):
    for year in [1, 1900, 2500]:
      expect(calling(process_common.score, 'word', 10, year)).to(equal(0))

  with it('score unaffected for year 0 or valid years'):
    for year in [0, 1990, 2018]:
      expect(calling(process_common.score, 'word', 10, year)).not_to(equal(0))

  with it('scores 0 for repeated letters'):
    for word in ['aaa', 'xxxword', 'errror']:
      expect(calling(process_common.score, word, 10, 0)).to(equal(0))

  with it('scores 0 for banned letters'):
    for word in ['garbage$input', '@asdf', '#tag', 'white space']:
      expect(calling(process_common.score, word, 10, 0)).to(equal(0))

  with it('punishes all-caps'):
    expect(process_common.score('WORD', 10, 0)).to(be_below(10))

  with it('negates TitleCase'):
    expect(process_common.score('TitleCase', 10, 0)).to(be_below(0))

  with it('severely punishes camelCase'):
    expect(process_common.score('camelCase', 10, 0)).to(equal(0))

  with it('scores words with few vowels lower'):
    expect(process_common.score('rhythm', 10, 0)).to(be_below(10))

  with it('does not punish words with many duplicates'):
    expect(process_common.score('balloon', 10, 0)).to(equal(10))


with description('aggregate_prefixes') as self:
  with before.each:
    self.subject = lambda *a: list(process_common.aggregate_prefixes(list(a)))

  with it('should produce no output for empty input'):
    expect(self.subject([])).to(equal([]))
    expect(self.subject([], [])).to(equal([]))

  with it('should return first elements for single stream'):
    expect(self.subject(['a', 'b', 'c'])).to(equal([
      ('a', None), ('b', None), ('c', None)]))

  with it('should invent elements if first stream is empty'):
    expect(self.subject([], ['a c', 'b b', 'c a'])).to(equal([
      ('a', [('a c', None)]),
      ('b', [('b b', None)]),
      ('c', [('c a', None)]),
    ]))

  with it('should ensure prefixes from distant streams'):
    expect(self.subject([], [], [], ['a b c d'])).to(equal([
      ('a', [('a b', [('a b c', [('a b c d', None)])])]),
    ]))

  with it('handles regression'):
    expect(self.subject(
        ['a'], ['a ba'], ['a babe in'], ['a babe in the'],
        ['a babe in the woods'])
    ).to(equal([
        ('a', [
          ('a ba', []),
          ('a babe', [
            ('a babe in', [
              ('a babe in the', [
                ('a babe in the woods', None),
              ]),
            ]),
          ]),
        ]),
    ]))

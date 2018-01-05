from data import process_common
from spec.mamba import *


with description('process_common'):
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

from expects import *
from src.origen import seven_segment_data


with description('alphabet'):
  with it('loads the alphabet'):
    expect(seven_segment_data.ALPHABET).to(have_keys('A', 'a', 'b', 'C', 'c'))

with description('words'):
  with it('loads the dictionary groups'):
    words = seven_segment_data.ACCESS_WORDS
    expect(words).to(have_keys('POSITIVE', 'NEGATIVE', 'FALSE_POSITIVE'))

  with it('loads ACCESS words from dictionary group'):
    words = seven_segment_data.ACCESS_WORDS
    expect(words['POSITIVE']).to(have_keys('ACCESS'))
    expect(words['POSITIVE']['ACCESS']).to(equal(seven_segment_data.ACCESS))

  with it('loads NEGATIVE words from dictionary group'):
    words = seven_segment_data.ACCESS_WORDS
    expect(words['NEGATIVE']).to_not(be_empty)
    expect(words['NEGATIVE']).to(have_keys('Err', 'fail', 'FAIL'))

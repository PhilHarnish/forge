from expects import *
from src.origen import seven_segment_data


with description('alphabet'):
  with it('loads the alphabet'):
    expect(seven_segment_data.ALPHABET).to(have_keys('A', 'a', 'b', 'C', 'c'))

with description('words'):
  with it('loads the dictionary'):
    words = seven_segment_data.ACCESS_WORDS
    expect(words).to(have_keys('POSITIVE', 'NEGATIVE', 'FALSE_POSITIVE'))

from expects import *
from src.origen import seven_segment_data


with description('alphabet'):
  with it('loads a the dictionary'):
    alphabet = seven_segment_data.alphabet()
    expect(alphabet).to(have_keys('A', 'a', 'b', 'C', 'c'))

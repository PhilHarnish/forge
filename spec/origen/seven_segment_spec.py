from expects import *
from src.origen import seven_segment

_DASH = """[-]
###
"""

_A = """[a]
###
  #
###
# #
###
"""
_C = """[c]


###
#
###
"""

with description('parse'):
  with it('parses simple input'):
    letter = seven_segment.parse(_DASH)
    expect(letter.ascii).to(equal('-'))
    expect(letter.segments).to(equal([0, 1, 0]))

  with it('parses fixed width text'):
    letter = seven_segment.parse(_A)
    expect(letter.ascii).to(equal('a'))
    expect(letter.segments).to(equal([2, 7, 3]))

  with it('parses input with blank lines'):
    letter = seven_segment.parse(_C)
    expect(letter.ascii).to(equal('c'))
    expect(letter.segments).to(equal([2, 6, 0]))


with description('load'):
  with it('handles simple input'):
    alphabet = seven_segment.load(_DASH)
    expect(alphabet).to(have_key('-'))

  with it('handles multiple lines'):
    input = '\n'.join([_DASH, _A, _C])
    alphabet = seven_segment.load(input)
    expect(alphabet).to(have_keys('-', 'a', 'c'))

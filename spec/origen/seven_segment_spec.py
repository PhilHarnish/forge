from expects import *
from src.origen import seven_segment

_DASH = """[-]
###
""".split('\n')

_A = """[a]
###
  #
###
# #
###
""".split('\n')

_C = """[c]


###
#
###
""".split('\n')


def _test(letter):
  # Perform operations normally handled by "data" module.
  return letter[0].strip('[]'), letter[1:]


with description('parse'):

  with it('parses simple input'):
    letter = seven_segment.Glyph(*_test(_DASH))
    expect(letter.name).to(equal('-'))
    expect(letter.segments).to(equal([0, 1, 0]))

  with it('parses fixed width text'):
    letter = seven_segment.Glyph(*_test(_A))
    expect(letter.name).to(equal('a'))
    expect(letter.segments).to(equal([2, 7, 3]))

  with it('parses input with blank lines'):
    letter = seven_segment.Glyph(*_test(_C))
    expect(letter.name).to(equal('c'))
    expect(letter.segments).to(equal([2, 6, 0]))


with description('load'):
  with it('handles simple input'):
    alphabet = seven_segment.load(_DASH)
    expect(alphabet).to(have_key('-'))

  with it('handles multiple lines'):
    input = _DASH + _A + _C
    alphabet = seven_segment.load(input)
    expect(alphabet).to(have_keys('-', 'a', 'c'))

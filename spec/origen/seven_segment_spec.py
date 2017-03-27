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


with description('Glyphs'):

  with it('should construct without errors'):
    word = seven_segment.Glyphs('Test', [''])
    expect(word.name).to(equal('Test'))

  with it('should handle equality for Glyphs with identical segments'):
    dash1 = seven_segment.Glyphs('dash1', ['###'])
    dash2 = seven_segment.Glyphs('dash2', ['###'])
    pipe = seven_segment.Glyphs('pipe', ['#'] * 3)
    expect(dash1).to(equal(dash2))
    expect(dash1).to_not(equal(pipe))

  with it('should merge glyphs'):
    dash = seven_segment.Glyphs('_', ['', '', '###'])
    pipe = seven_segment.Glyphs('|', ['#'] * 3)
    expected = seven_segment.Glyphs('L', ['#'] * 2 + ['###'])
    expect(dash | pipe).to(equal(expected))

  with it('should concatenate full glyphs'):
    dash = seven_segment.Glyphs('dash', ['###'])
    expected = seven_segment.Glyphs('dash dash', ['### ###'])
    expect(dash + dash).to(equal(expected))

  with it('should concatenate partial glyphs'):
    dash = seven_segment.Glyphs('|', ['#'] * 3)
    expected = seven_segment.Glyphs('| |', ['# #'] * 3)
    expect(dash + dash).to(equal(expected))

  with it('should erase segments if shifted away'):
    bar = seven_segment.Glyphs('|', ['#'] * 3)
    empty = seven_segment.Glyphs('', [])
    expect(bar << 1).to(equal(empty))

  with it('should shift left'):
    bars = seven_segment.Glyphs('| |', ['# #'] * 3)
    bar = seven_segment.Glyphs('|', ['#'] * 3)
    expect(bars << 1).to(equal(bar))

  with it('should shift right'):
    bar = seven_segment.Glyphs('|', ['#'] * 3)
    right_bar = seven_segment.Glyphs('  |', ['  #'] * 3)
    expect(bar >> 1).to(equal(right_bar))

  with it('should return len()'):
    dash = seven_segment.Glyphs('-', ['###'])
    expect(len(dash)).to(equal(3))


with description('parse'):

  with it('parses simple input'):
    letter = seven_segment.Glyphs(*_test(_DASH))
    expect(letter.name).to(equal('-'))
    expect(letter.segments).to(equal([0, 1, 0]))

  with it('parses fixed width text'):
    letter = seven_segment.Glyphs(*_test(_A))
    expect(letter.name).to(equal('a'))
    expect(letter.segments).to(equal([2, 7, 3]))

  with it('parses input with blank lines'):
    letter = seven_segment.Glyphs(*_test(_C))
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

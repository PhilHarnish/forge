from data.graph import bloom_node, regex
from spec.mamba import *

_GOAL = "BloomNode('', '#', 1)"


with description('parse'):
  with it('rejects unsupported input'):
    expect(calling(regex.parse, 'multiple words')).to(
        raise_error(NotImplementedError))
    expect(calling(regex.parse, '(matching group)')).to(
        raise_error(NotImplementedError))
    expect(calling(regex.parse, '[char group]')).to(
        raise_error(NotImplementedError))
    expect(calling(regex.parse, 'a|b')).to(
        raise_error(NotImplementedError, 'Unsupported characters in a|b ("|")'))
    expect(calling(regex.parse, 'a*')).to(
        raise_error(NotImplementedError, 'Unsupported characters in a* ("*")'))
    expect(calling(regex.parse, 'a+')).to(
        raise_error(NotImplementedError, 'Unsupported characters in a+ ("+")'))

  with it('accepts simple input'):
    expect(calling(regex.parse, 'simple')).not_to(raise_error)
    expect(calling(regex.parse, 's.mple')).not_to(raise_error)

  with it('produces simple graphs'):
    parsed = regex.parse('a')
    expect(parsed).to(be_a(bloom_node.BloomNode))
    expect(repr(parsed)).to(equal("BloomNode('A', ' #', 0)"))
    expect(repr(parsed['a'])).to(equal(_GOAL))

  with it('produces longer graphs'):
    parsed = regex.parse('abc')
    expect(parsed).to(be_a(bloom_node.BloomNode))
    expect(repr(parsed)).to(equal("BloomNode('ABC', '   #', 0)"))
    expect(repr(parsed['a']['b']['c'])).to(equal(_GOAL))

  with description('with "." character'):
    with it('produces simple graphs'):
      parsed = regex.parse('.')
      expect(parsed).to(be_a(bloom_node.BloomNode))
      expect(repr(parsed)).to(equal(
          "BloomNode('abcdefghijklmnopqrstuvwxyz', ' #', 0)"))
      expect(repr(parsed['z'])).to(equal(_GOAL))

    with it('produces wildcard prefix'):
      parsed = regex.parse('.b')
      expect(parsed).to(be_a(bloom_node.BloomNode))
      expect(repr(parsed)).to(equal(
          "BloomNode('aBcdefghijklmnopqrstuvwxyz', '  #', 0)"))
      expect(repr(parsed['z'])).to(equal("BloomNode('B', ' #', 0)"))
      expect(repr(parsed['z']['b'])).to(equal(_GOAL))

    with it('produces wildcard suffix'):
      parsed = regex.parse('a.')
      expect(parsed).to(be_a(bloom_node.BloomNode))
      expect(repr(parsed)).to(equal(
          "BloomNode('Abcdefghijklmnopqrstuvwxyz', '  #', 0)"))
      expect(repr(parsed['a']['z'])).to(equal(_GOAL))

    with it('produces wildcard middle'):
      parsed = regex.parse('a.c')
      expect(parsed).to(be_a(bloom_node.BloomNode))
      expect(repr(parsed)).to(equal(
          "BloomNode('AbCdefghijklmnopqrstuvwxyz', '   #', 0)"))
      expect(repr(parsed['a']['z'])).to(equal("BloomNode('C', ' #', 0)"))
      expect(repr(parsed['a']['z']['c'])).to(equal(_GOAL))

    with it('does not accept invalid paths through graph'):
      parsed = regex.parse('a.c')
      expect(lambda: parsed['a']['z']['z']).to(raise_error(KeyError))

with description('normalize'):
  with it('leaves normal input alone'):
    expect(regex.normalize('asdf')).to(equal('asdf'))

  with it('converts ALL CAPS'):
    expect(regex.normalize('ALL CAPS')).to(equal('all caps'))

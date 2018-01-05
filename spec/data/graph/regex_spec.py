from data.graph import bloom_node, regex
from spec.mamba import *

_GOAL = "BloomNode('', '#', 1)"


with fdescription('parse'):
  with it('rejects unsupported input'):
    expect(calling(regex.parse, '[char group]')).to(
        raise_error(NotImplementedError))
    expect(calling(regex.parse, '(matching group)')).to(
        raise_error(NotImplementedError))
    expect(calling(regex.parse, 'a*')).to(
        raise_error(NotImplementedError, 'Unsupported re type MAX_REPEAT'))
    expect(calling(regex.parse, 'a+')).to(
        raise_error(NotImplementedError, 'Unsupported re type MAX_REPEAT'))

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

  with description('with capitals'):
    with it('produces simple graphs'):
      parsed = regex.parse('aA')
      expect(repr(parsed)).to(equal("BloomNode('A;A', '  #', 0)"))

    with it('with "."'):
      parsed = regex.parse('a.Z')
      expect(repr(parsed)).to(equal(
          "BloomNode('Abcdefghijklmnopqrstuvwxyz;ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
          " '   #', 0)"))

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
      expect(repr(parsed)).to(equal(
          "BloomNode('AbCdefghijklmnopqrstuvwxyz', '   #', 0)"))
      expect(lambda: parsed['a']['z']['z']).to(raise_error(KeyError))

  with description('whitespace'):
    with it('accepts simple example'):
      expect(calling(regex.parse, 'multiple words')).not_to(raise_error)

    with it('produces simple graphs'):
      parsed = regex.parse('a b')
      expect(repr(parsed)).to(equal("BloomNode('A; ', ' #', 0)"))
      expect(repr(parsed['a'])).to(equal("BloomNode(' ', '#', 0)"))
      expect(repr(parsed['a'][' '])).to(equal("BloomNode('B', ' #', 0)"))
      expect(repr(parsed['a'][' ']['b'])).to(equal(_GOAL))

  with description('regex'):
    with it('supports small character groups'):
      node = regex.parse('[abc][def]')
      expect(repr(node)).to(equal("BloomNode('abcdef', '  #', 0)"))
      expect(repr(node['a'])).to(equal("BloomNode('def', ' #', 0)"))

    with it('supports small A|B expressions'):
      expect(repr(regex.parse('a|b'))).to(equal("BloomNode('ab', ' #', 0)"))

with description('normalize'):
  with it('leaves normal input alone'):
    expect(regex.normalize('asdf')).to(equal('asdf'))

  with it('converts ALL CAPS'):
    expect(regex.normalize('ALL CAPS')).to(equal('all caps'))

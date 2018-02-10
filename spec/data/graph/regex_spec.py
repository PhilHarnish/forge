from data.graph import bloom_node, regex
from spec.mamba import *

_GOAL = "BloomNode('', '#', 1)"


with description('parse'):
  with it('rejects unsupported input'):
    expect(calling(regex.parse, 'a*')).to(
        raise_error(NotImplementedError, 'Unable to repeat MAXREPEAT'))
    expect(calling(regex.parse, 'a+')).to(
        raise_error(NotImplementedError, 'Unable to repeat MAXREPEAT'))

  with it('produces simple graphs'):
    node = regex.parse('a')
    expect(node).to(be_a(bloom_node.BloomNode))
    expect(path_values(node, 'a')).to(look_like("""
        BloomNode('A', ' #', 0)
        a = BloomNode('', '#', 1)
    """))

  with it('produces longer graphs'):
    node = regex.parse('abc')
    expect(node).to(be_a(bloom_node.BloomNode))
    expect(path_values(node, 'abc')).to(look_like("""
        BloomNode('ABC', '   #', 0)
        a = BloomNode('BC', '  #', 0)
        b = BloomNode('C', ' #', 0)
        c = BloomNode('', '#', 1)
    """))

  with description('with capitals'):
    with it('produces simple graphs'):
      node = regex.parse('aA')
      expect(path_values(node, 'aA')).to(look_like("""
          BloomNode('A;A', '  #', 0)
          a = BloomNode('A', ' #', 0)
          A = BloomNode('', '#', 1)
      """))

    with it('with "."'):
      node = regex.parse('a.Z')
      expect(path_values(node, 'azZ')).to(look_like("""
BloomNode('Abcdefghijklmnopqrstuvwxyz;ABCDEFGHIJKLMNOPQRSTUVWXYZ', '   #', 0)
a = BloomNode('abcdefghijklmnopqrstuvwxyz;ABCDEFGHIJKLMNOPQRSTUVWXYZ', '  #', 0)
z = BloomNode('Z', ' #', 0)
Z = BloomNode('', '#', 1)
      """))

  with description('with "." character'):
    with it('produces simple graphs'):
      node = regex.parse('.')
      expect(path_values(node, 'z')).to(look_like("""
          BloomNode('abcdefghijklmnopqrstuvwxyz', ' #', 0)
          z = BloomNode('', '#', 1)
      """))

    with it('produces wildcard prefix'):
      node = regex.parse('.b')
      expect(path_values(node, 'zb')).to(look_like("""
          BloomNode('aBcdefghijklmnopqrstuvwxyz', '  #', 0)
          z = BloomNode('B', ' #', 0)
          b = BloomNode('', '#', 1)
      """))

    with it('produces wildcard suffix'):
      node = regex.parse('a.')
      expect(path_values(node, 'az')).to(look_like("""
          BloomNode('Abcdefghijklmnopqrstuvwxyz', '  #', 0)
          a = BloomNode('abcdefghijklmnopqrstuvwxyz', ' #', 0)
          z = BloomNode('', '#', 1)
      """))

    with it('produces wildcard middle'):
      node = regex.parse('a.c')
      expect(path_values(node, 'azc')).to(look_like("""
          BloomNode('AbCdefghijklmnopqrstuvwxyz', '   #', 0)
          a = BloomNode('abCdefghijklmnopqrstuvwxyz', '  #', 0)
          z = BloomNode('C', ' #', 0)
          c = BloomNode('', '#', 1)
      """))

    with it('does not accept invalid paths through graph'):
      parsed = regex.parse('a.c')
      expect(repr(parsed)).to(equal(
          "BloomNode('AbCdefghijklmnopqrstuvwxyz', '   #', 0)"))
      expect(lambda: parsed['a']['z']['z']).to(raise_error(KeyError))

  with description('whitespace'):
    with it('accepts simple example'):
      expect(calling(regex.parse, 'multiple words')).not_to(raise_error)

    with it('produces simple graphs'):
      node = regex.parse('a b')
      expect(path_values(node, 'a b')).to(look_like("""
        BloomNode('A; ', ' #', 0)
        a = BloomNode(' ', '#', 0)
          = BloomNode('B', ' #', 0)
        b = BloomNode('', '#', 1)
      """))

  with it('supports small character groups'):
    node = regex.parse('[abc][def]')
    expect(path_values(node, 'ae')).to(look_like("""
        BloomNode('abcdef', '  #', 0)
        a = BloomNode('def', ' #', 0)
        e = BloomNode('', '#', 1)
    """))

  with it('supports character groups with spaces'):
    node = regex.parse('[abc][abc ][abc]')
    expect(path_values(node, 'a b')).to(look_like("""
        BloomNode('abc; ', ' # #', 0)
        a = BloomNode('abc; ', '# #', 0)
          = BloomNode('abc', ' #', 0)
        b = BloomNode('', '#', 1)
    """))

  with it('supports small A|B expressions'):
    expect(repr(regex.parse('a|b'))).to(equal("BloomNode('ab', ' #', 0)"))

  with it('supports optional (x?) characters'):
    node = regex.parse('abc?')
    expect(path_values(node, 'abc')).to(look_like("""
        BloomNode('ABc', '  ##', 0)
        a = BloomNode('Bc', ' ##', 0)
        b = BloomNode('C', '##', 1)
        c = BloomNode('', '#', 1)
    """))

  with it('supports repeat ranges'):
    node = regex.parse('ab{1,3}')
    expect(path_values(node, 'abbb')).to(look_like("""
        BloomNode('AB', '  ###', 0)
        a = BloomNode('B', ' ###', 0)
        b = BloomNode('B', '###', 1)
        b = BloomNode('B', '##', 1)
        b = BloomNode('', '#', 1)
    """))

  with it('supports repeat ranges + suffix'):
    node = regex.parse('b{1,3}c')
    expect(path_values(node, 'bbbc')).to(look_like("""
        BloomNode('BC', '  ###', 0)
        b = BloomNode('bC', ' ###', 0)
        b = BloomNode('bC', ' ##', 0)
        b = BloomNode('C', ' #', 0)
        c = BloomNode('', '#', 1)
    """))
    expect(repr(node['b']['c'])).to(equal(_GOAL))
    expect(repr(node['b']['b']['c'])).to(equal(_GOAL))
    expect(repr(node['b']['b']['b']['c'])).to(equal(_GOAL))

  with it('supports simple capture groups'):
    expect(calling(regex.parse, '(abc)')).not_to(raise_error)
    node = regex.parse('(abc)')
    expect(path_values(node, 'abc')).to(look_like("""
        BloomNode('ABC', '   #', 0, ENTER_1=1)
        a = BloomNode('BC', '  #', 0)
        b = BloomNode('C', ' #', 0)
        c = BloomNode('', '#', 1, EXIT_1=1)
    """))

  with it('supports named capture groups'):
    node = regex.parse('(?P<id>abc)')
    expect(path_values(node, 'abc')).to(look_like("""
        BloomNode('ABC', '   #', 0, ENTER_id=1)
        a = BloomNode('BC', '  #', 0)
        b = BloomNode('C', ' #', 0)
        c = BloomNode('', '#', 1, EXIT_id=1)
    """))

  with it('parses anagram syntax'):
    expect(calling(regex.parse, '{ab,c}')).not_to(raise_error)
    node = regex.parse('{ab,c}')
    expect(path_values(node, 'cab')).to(look_like("""
        BloomNode('ABC', '   #', 0)
        c = BloomNode('AB', '  #', 0)
        a = BloomNode('B', ' #', 0)
        b = BloomNode('', '#', 1)
    """))
    expect(path_values(node, 'abc')).to(look_like("""
        BloomNode('ABC', '   #', 0)
        a = BloomNode('BC', '  #', 0)
        b = BloomNode('C', ' #', 0)
        c = BloomNode('', '#', 1)
    """))
    expect(lambda: node['bac']).to(raise_error(KeyError))

  with it('parses anagram syntax with prefix/suffix'):
    expect(calling(regex.parse, 'd{abc}e')).not_to(raise_error)
    node = regex.parse('d{abc}e')
    expect(path_values(node, 'dcabe')).to(look_like("""
        BloomNode('ABCDE', '     #', 0)
        d = BloomNode('ABCE', '    #', 0)
        c = BloomNode('ABE', '   #', 0)
        a = BloomNode('BE', '  #', 0)
        b = BloomNode('E', ' #', 0)
        e = BloomNode('', '#', 1)
    """))
    expect(repr(node['d']['a']['b']['c'])).to(equal("BloomNode('E', ' #', 0)"))
    expect(lambda: node['dabca']).to(raise_error(KeyError))

  with it('parses anagram syntax with spaces'):
    expect(calling(regex.parse, '{noti }')).not_to(raise_error)
    node = regex.parse('{noti }')
    expect(path_values(node, 'not i')).to(look_like("""
        BloomNode('inot; !', ' ###', 0)
        n = BloomNode('iot; !', '###', 0)
        o = BloomNode('it; !', '##', 0)
        t = BloomNode('i; !', '#', 0)
          = BloomNode('I', ' #', 0)
        i = BloomNode('', '#', 1)
    """))
    expect(path_values(node, 'i not')).to(look_like("""
        BloomNode('inot; !', ' ###', 0)
        i = BloomNode('not; !', '###', 0)
          = BloomNode('NOT', '   #', 0)
        n = BloomNode('OT', '  #', 0)
        o = BloomNode('T', ' #', 0)
        t = BloomNode('', '#', 1)
    """))
    expect(path_values(node, 'in to')).to(look_like("""
        BloomNode('inot; !', ' ###', 0)
        i = BloomNode('not; !', '###', 0)
        n = BloomNode('ot; !', '##', 0)
          = BloomNode('OT', '  #', 0)
        t = BloomNode('O', ' #', 0)
        o = BloomNode('', '#', 1)
    """))

  with it('parses anagram regex'):
    expect(calling(regex.parse, '{abc.}')).not_to(raise_error)
    node = regex.parse('{abc.}')
    expect(path_values(node, 'zabc')).to(look_like("""
        BloomNode('ABCdefghijklmnopqrstuvwxyz', '    #', 0)
        z = BloomNode('ABC', '   #', 0, anagrams=AnagramIter(todo, todo, todo))
        a = BloomNode('BC', '  #', 0, anagrams=AnagramIter(todo, todo))
        b = BloomNode('C', ' #', 0)  # NB: AnagramIter(todo) optimized away.
        c = BloomNode('', '#', 1)
    """, remove_comments=True))


with description('normalize'):
  with it('leaves normal input alone'):
    expect(regex.normalize('asdf')).to(equal('asdf'))

  with it('converts ALL CAPS'):
    expect(regex.normalize('ALL CAPS')).to(equal('all caps'))

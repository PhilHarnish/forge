from data.graph import bloom_node
from data.graph.ops import anagram_transform_op
from spec.mamba import *


_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


class Transformer(object):
  def __init__(self, name: str) -> None:
    self._name = name
    self._path = name.rstrip('?')
    self._optional = name.endswith('?')

  def __call__(self, node: bloom_node.BloomNode) -> bloom_node.BloomNode:
    start = node
    for c in reversed(self._path):
      next_node = bloom_node.BloomNode()
      if c == '.':
        next_node.links(_ALPHABET, node)
      elif c == ' ':
        # Space support is case-by-case.
        next_node.link(c, node)
        # Require spaces for this test.
        next_node.require_mask = next_node.provide_mask
        # Allow space to mark a completed node (makes a more interesting test).
        node.distance(0)
        node.match_weight = node.max_weight
      else:
        next_node.link(c, node)
      node = next_node
    if self._optional:
      return node + start
    return node

  def __str__(self) -> str:
    return self._name

  __repr__ = __str__


with description('anagram transform op merge') as self:
  with before.each:
    self.host = bloom_node.BloomNode()
    self.exit = bloom_node.BloomNode()
    self.exit.distance(0)
    self.exit.weight(1, True)
    self.sources = [self.exit]

  with it('merges top level'):
    anagram_transform_op.merge_fn(
        self.host, self.sources, [[Transformer('a'), Transformer('b')]])
    expect(repr(self.host)).to(equal("BloomNode('AB', '  #', 0)"))

  with it('merges with decreasing distance'):
    anagram_transform_op.merge_fn(
        self.host, self.sources, [[Transformer('a'), Transformer('b')]])
    expect(path_values(self.host, 'ab')).to(look_like("""
        BloomNode('AB', '  #', 0)
        a = BloomNode('B', ' #', 0)  # NB: AnagramIter(b) optimized away.
        b = BloomNode('', '#', 1)
    """, remove_comments=True))

  with it('handles duplicates'):
    a = Transformer('a')
    b = Transformer('b')
    anagram_transform_op.merge_fn(
        self.host, self.sources, [[a, a, b]])
    expect(path_values(self.host, 'baa')).to(look_like("""
        BloomNode('AB', '   #', 0)
        b = BloomNode('A', '  #', 0)  # NB: AnagramIter(a*2) optimized away.
        a = BloomNode('A', ' #', 0)  # NB: AnagramIter(a) optimized away.
        a = BloomNode('', '#', 1)
    """, remove_comments=True))

  with it('handles complex options'):
    abc = Transformer('abc')
    bcd = Transformer('.bcd')
    d = Transformer('d')
    anagram_transform_op.merge_fn(self.host, self.sources, [[abc, bcd, d]])
    # Clear paths.
    expect(path_values(self.host, 'zbcddabc')).to(look_like("""
        BloomNode('ABCDefghijklmnopqrstuvwxyz', '        #', 0)
        z = BloomNode('ABCD', '       #', 0)
        b = BloomNode('ABCD', '      #', 0)
        c = BloomNode('ABCD', '     #', 0)
        d = BloomNode('ABCD', '    #', 0, anagrams=AnagramIter(abc, d))
        d = BloomNode('ABC', '   #', 0)  # NB: AnagramIter(abc) optimized away.
        a = BloomNode('BC', '  #', 0)
        b = BloomNode('C', ' #', 0)
        c = BloomNode('', '#', 1)
    """, remove_comments=True))
    # Ambiguous paths.
    expect(path_values(self.host, 'abcdabcd')).to(look_like("""
        BloomNode('ABCDefghijklmnopqrstuvwxyz', '        #', 0)
        a = BloomNode('aBCDefghijklmnopqrstuvwxyz', '       #', 0)
        b = BloomNode('aBCDefghijklmnopqrstuvwxyz', '      #', 0)
        c = BloomNode('aBCDefghijklmnopqrstuvwxyz', '     #', 0, anagrams=AnagramIter(.bcd, d))
        # NB: AnagramIter(.bcd) optimized away in next node:
        d = BloomNode('aBCDefghijklmnopqrstuvwxyz', '    #', 0, anagrams=AnagramIter(abc, d))
        a = BloomNode('BCD', '   #', 0)
        b = BloomNode('CD', '  #', 0)
        c = BloomNode('D', ' #', 0)  # NB: AnagramIter(d) optimized away.
        d = BloomNode('', '#', 1)
    """, remove_comments=True))

  with it('handles optional characters'):
    abc = Transformer('abc?')
    a = Transformer('a')
    b = Transformer('b')
    c = Transformer('c')
    anagram_transform_op.merge_fn(self.host, self.sources, [[abc, a, b, c]])
    # Clear paths.
    expect(path_values(self.host, 'cababc')).to(look_like("""
        BloomNode('ABC', '   #  #', 0)
        c = BloomNode('ABc', '  #  #', 0, anagrams={AnagramIter(a, abc?, b), AnagramIter(a, b)})
        a = BloomNode('aBc', ' #  #', 0, anagrams=AnagramIter(abc?, b))
        b = BloomNode('ABC', '#  #', 1)  # Exit while skipping "abc?".
        a = BloomNode('BC', '  #', 0)
        b = BloomNode('C', ' #', 0)
        c = BloomNode('', '#', 1)
    """, remove_comments=True))
    expect(path_values(self.host, 'caabcb')).to(look_like("""
        BloomNode('ABC', '   #  #', 0)
        c = BloomNode('ABc', '  #  #', 0, anagrams={AnagramIter(a, abc?, b), AnagramIter(a, b)})
        a = BloomNode('aBc', ' #  #', 0, anagrams=AnagramIter(abc?, b))
        a = BloomNode('BC', '   #', 0)
        b = BloomNode('BC', '  #', 0)
        c = BloomNode('B', ' #', 0)
        b = BloomNode('', '#', 1)
    """))
    # Ambiguous paths.
    expect(path_values(self.host, 'abcabc')).to(look_like("""
        BloomNode('ABC', '   #  #', 0)
        a = BloomNode('aBC', '  #  #', 0, anagrams={AnagramIter(abc?, b, c), AnagramIter(b, c)})
        b = BloomNode('abC', ' #  #', 0, anagrams=AnagramIter(abc?, c))
        c = BloomNode('ABC', '#  #', 1, anagrams=AnagramIter(a, b, c))
        a = BloomNode('BC', '  #', 0, anagrams=AnagramIter(b, c))
        b = BloomNode('C', ' #', 0)
        c = BloomNode('', '#', 1)
    """))

  with it('handles spaces'):
    space = Transformer(' ')
    a = Transformer('a')
    b = Transformer('b')
    c = Transformer('c')
    anagram_transform_op.merge_fn(self.host, self.sources, [[space, a, b, c]])
    expect(path_values(self.host, 'a bc')).to(look_like("""
        BloomNode('abc; !', '', 0)
        a = BloomNode('bc; !', '', 0, anagrams=AnagramIter( , b, c))
          = BloomNode('BC', '# #', 1, anagrams=AnagramIter(b, c))
        b = BloomNode('C', ' #', 0)
        c = BloomNode('', '#', 1)
    """))

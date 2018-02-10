from data.graph import bloom_node
from data.graph.ops import anagram_transform_op
from spec.mamba import *


_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


class Transformer(object):
  def __init__(self, name: str) -> None:
    self._name = name

  def __call__(self, node: bloom_node.BloomNode) -> bloom_node.BloomNode:
    for c in reversed(self._name):
      next_node = bloom_node.BloomNode()
      if c == '.':
        next_node.links(_ALPHABET, node)
      else:
        next_node.link(c, node)
      node = next_node
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
    anagram_transform_op.merge_fn(
        self.host, self.sources, [[abc, bcd, d]])
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

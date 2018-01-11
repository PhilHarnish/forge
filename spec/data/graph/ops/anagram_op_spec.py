from data.graph import bloom_node
from data.graph.ops import anagram_op
from spec.mamba import *


with description('anagram op merge') as self:
  with before.each:
    self.host = bloom_node.BloomNode()
    self.exit = bloom_node.BloomNode()
    self.exit.distance(0)
    self.exit.weight(1, True)
    self.sources = [self.exit]
    self.extra = [['ab', 'c']]

  with it('merges top level'):
    anagram_op.merge_fn(self.host, self.sources, self.extra)
    expect(repr(self.host)).to(equal("BloomNode('ABC', '   #', 0)"))

  with it('merges with decreasing distance'):
    anagram_op.merge_fn(self.host, self.sources, self.extra)
    child = self.host['c']
    expect(repr(child)).to(equal("BloomNode('AB', '  #', 0)"))

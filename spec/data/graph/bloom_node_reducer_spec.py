from data.graph import _op_mixin, bloom_node, bloom_node_reducer, trie
from spec.mamba import *

with description('reduce'):
  with it('is a no-op for empty input'):
    op = _op_mixin.IDENTITY
    expect(list(bloom_node_reducer.reduce(op))).to(equal([]))

  with description('OP_IDENTITY'):
    with it('reduces IDENTITY to itself'):
      node = bloom_node.BloomNode()
      child = node.open('key')
      op = _op_mixin.Op(_op_mixin.OP_IDENTITY, [node])
      expect(list(bloom_node_reducer.reduce(op))).to(equal([
        ('key', child),
      ]))

    with it('raises for IDENTITY + multiple sources'):
      node = bloom_node.BloomNode()
      node.open('key')
      op = _op_mixin.Op(_op_mixin.OP_IDENTITY, [node, node])
      expect(calling(next, bloom_node_reducer.reduce(op))).to(
          raise_error(NotImplementedError))

  with description('OP_ADD') as self:
    with description('two simple sources'):
      with before.each:
        a = bloom_node.BloomNode()
        trie.add(a, 'a', 1)
        trie.add(a, 'c', .75)
        b = bloom_node.BloomNode()
        trie.add(b, 'b', 1)
        trie.add(b, 'c', .5)
        self.node = a + b

      with it('provides all branches'):
        results = list(sorted(
            bloom_node_reducer.reduce(self.node.op), key=lambda x: x[0]))
        expect(str(results)).to(
            equal(
                "[('a', BloomNode('', '#', 1)),"
                " ('b', BloomNode('', '#', 1)),"
                " ('c', BloomNode('', '#', 0.75))]"))

      with it('combines with a third'):
        c = bloom_node.BloomNode()
        trie.add(c, 'c', 1)
        trie.add(c, 'd', .25)
        node = self.node + c
        results = list(sorted(
            bloom_node_reducer.reduce(node.op), key=lambda x: x[0]))
        expect(str(results)).to(
            equal(
                "[('a', BloomNode('', '#', 1)),"
                " ('b', BloomNode('', '#', 1)),"
                " ('c', BloomNode('', '#', 1)),"
                " ('d', BloomNode('', '#', 0.25))]"))

    with description('two larger sources'):
      with before.each:
        a = bloom_node.BloomNode()
        trie.add(a, 'aonly', 1)
        trie.add(a, 'com', .8)
        trie.add(a, 'common', .75)
        b = bloom_node.BloomNode()
        trie.add(b, 'bonly', 1)
        trie.add(b, 'com', .25)
        trie.add(b, 'common', .5)
        self.node = a + b

      with it('adds two sources, recursively'):
        expecteds = [
          # START.
          "[('a', BloomNode('LNOY', '    #', 0)),"
              " ('b', BloomNode('LNOY', '    #', 0)),"
              " ('c', BloomNode('MnO', '  #  #', 0))]",
          # -> c.
          "[('o', BloomNode('Mno', ' #  #', 0))]",
          # -> o.
          "[('m', BloomNode('mNO', '#  #', 0.8))]",
          # -> m.
          "[('m', BloomNode('NO', '  #', 0))]",
          # -> m.
          "[('o', BloomNode('N', ' #', 0))]",
          # -> o.
          "[('n', BloomNode('', '#', 0.75))]",
          # -> n.
        ]
        node = self.node
        for c, expected in zip('common', expecteds):
          results = list(sorted(
              bloom_node_reducer.reduce(node.op), key=lambda x: x[0]))
          expect(str(results)).to(equal(expected))
          node = node[c]
        # Ends at end of "common".
        expect(repr(node)).to(equal("BloomNode('', '#', 0.75)"))

      with it('provides solutions from other branches'):
        expecteds = [
          # START.
          "[('a', BloomNode('LNOY', '    #', 0)),"
              " ('b', BloomNode('LNOY', '    #', 0)),"
              " ('c', BloomNode('MnO', '  #  #', 0))]",
          # -> a.
          "[('o', BloomNode('LNY', '   #', 0))]",
          # -> o.
          "[('n', BloomNode('LY', '  #', 0))]",
          # -> n.
          "[('l', BloomNode('Y', ' #', 0))]",
          # -> l.
          "[('y', BloomNode('', '#', 1))]",
          # -> y.
        ]
        node = self.node
        for c, expected in zip('aonly', expecteds):
          results = list(sorted(
              bloom_node_reducer.reduce(node.op), key=lambda x: x[0]))
          expect(str(results)).to(equal(expected))
          node = node[c]
        # Ends at end of "common".
        expect(repr(node)).to(equal("BloomNode('', '#', 1)"))

  with description('OP_MULTIPLY'):
    with it('multiplies two sources'):
      a = bloom_node.BloomNode()
      trie.add(a, 'a', 1)
      trie.add(a, 'c', .5)
      b = bloom_node.BloomNode()
      trie.add(b, 'b', 1)
      trie.add(b, 'c', .5)
      node = a * b
      expect(str(list(bloom_node_reducer.reduce(node.op)))).to(
          equal("[('c', BloomNode('', '#', 0.25))]"))

    with it('scales 1 source'):
      a = bloom_node.BloomNode()
      trie.add(a, 'a', 1)
      trie.add(a, 'c', .5)
      node = a * 0.5
      expect(str(list(bloom_node_reducer.reduce(node.op)))).to(
          equal(
              "[('a', BloomNode('', '#', 0.5)),"
              " ('c', BloomNode('', '#', 0.25))]"))

    with it('scales 2 sources'):
      a = bloom_node.BloomNode()
      trie.add(a, 'a', 1)
      trie.add(a, 'c', .5)
      b = bloom_node.BloomNode()
      trie.add(b, 'b', 1)
      trie.add(b, 'c', .5)
      node = a * b * 0.5
      expect(str(node.op)).to(
          equal("(BloomNode('ac', ' #', 0)*BloomNode('bc', ' #', 0)*0.5)"))
      expect(str(list(bloom_node_reducer.reduce(node.op)))).to(
          equal("[('c', BloomNode('', '#', 0.125))]"))

    with it('multiplies two sources, but not recursively'):
      a = bloom_node.BloomNode()
      trie.add(a, 'aonly', 1)
      trie.add(a, 'com', .8)
      trie.add(a, 'common', .5)
      b = bloom_node.BloomNode()
      trie.add(b, 'bonly', 1)
      trie.add(b, 'com', .25)
      trie.add(b, 'common', .5)
      node = a * b
      expecteds = [
        # START.
        "[('c', BloomNode('MnO', '  #  #', 0))]",
        # -> c.
        "[('o', BloomNode('Mno', ' #  #', 0))]",
        # -> o.
        "[('m', BloomNode('mNO', '#  #', 0.2))]",
        # -> m.
        "[('m', BloomNode('NO', '  #', 0))]",
        # -> m.
        "[('o', BloomNode('N', ' #', 0))]",
        # -> o.
        "[('n', BloomNode('', '#', 0.25))]",
        # -> n.
      ]
      for c, expected in zip('common', expecteds):
        expect(str(list(bloom_node_reducer.reduce(node.op)))).to(
            equal(expected))
        node = node[c]
      # Ends at end of "common".
      expect(repr(node)).to(equal("BloomNode('', '#', 0.25)"))

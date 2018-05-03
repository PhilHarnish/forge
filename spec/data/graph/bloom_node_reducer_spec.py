from data.graph import _op_mixin, bloom_node, bloom_node_reducer, trie
from spec.mamba import *

with description('merge'):
  with it('can merge top-level properties'):
    a = bloom_node.BloomNode()
    a.distance(0)
    a.weight(1, True)
    b = bloom_node.BloomNode()
    merged = a + b
    bloom_node_reducer.merge(merged)
    expect(repr(merged)).to(equal("BloomNode('', '#', 1)"))

with description('reduce'):
  with it('is a no-op for empty input'):
    host = bloom_node.BloomNode(_op_mixin.Op(_op_mixin.OP_IDENTITY, []))
    expect(list(bloom_node_reducer.reduce(host))).to(equal([]))

  with description('OP_IDENTITY'):
    with it('reduces IDENTITY to itself'):
      node = bloom_node.BloomNode()
      child = node.open('a')
      host = bloom_node.BloomNode(_op_mixin.Op(_op_mixin.OP_IDENTITY, [node]))
      expect(list(bloom_node_reducer.reduce(host))).to(equal([
        ('a', child),
      ]))

    with it('raises for IDENTITY + multiple sources'):
      node = bloom_node.BloomNode()
      node.open('a')
      host = bloom_node.BloomNode(_op_mixin.Op(_op_mixin.OP_IDENTITY, [node, node]))
      expect(calling(next, bloom_node_reducer.reduce(host))).to(
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
            bloom_node_reducer.reduce(self.node), key=lambda x: x[0]))
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
            bloom_node_reducer.reduce(node), key=lambda x: x[0]))
        expect(str(results)).to(
            equal(
                "[('a', BloomNode('', '#', 1)),"
                " ('b', BloomNode('', '#', 1)),"
                " ('c', BloomNode('', '#', 1)),"
                " ('d', BloomNode('', '#', 0.25))]"))

    with description('two larger sources') as self:
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
          "[('m', BloomNode('MNO', '#  #', 0.8))]",
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
              bloom_node_reducer.reduce(node), key=lambda x: x[0]))
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
          if node.op:
            items = bloom_node_reducer.reduce(node)
          else:
            items = node.items()
          results = list(sorted(items, key=lambda x: x[0]))
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
      expect(str(list(bloom_node_reducer.reduce(node)))).to(
          equal("[('c', BloomNode('', '#', 0.25))]"))

    with it('scales 1 source'):
      a = bloom_node.BloomNode()
      trie.add(a, 'a', 1)
      trie.add(a, 'c', .5)
      node = a * 0.5
      expect(str(list(bloom_node_reducer.reduce(node)))).to(
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
      expect(str(list(bloom_node_reducer.reduce(node)))).to(
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
      trie.add(b, 'co', .45)
      node = a * b
      expecteds = [
        # START.
        "[('c', BloomNode('MnO', '  #  #', 0))]",
        # -> c.
        "[('o', BloomNode('Mno', ' #  #', 0))]",
        # -> o.
        "[('m', BloomNode('MNO', '#  #', 0.2))]",
        # -> m.
        "[('m', BloomNode('NO', '  #', 0))]",
        # -> m.
        "[('o', BloomNode('N', ' #', 0))]",
        # -> o.
        "[('n', BloomNode('', '#', 0.25))]",
        # -> n.
      ]
      for c, expected in zip('common', expecteds):
        expect(str(list(bloom_node_reducer.reduce(node)))).to(
            equal(expected))
        node = node[c]
      # Ends at end of "common".
      expect(repr(node)).to(equal("BloomNode('', '#', 0.25)"))

  with description('OP_CALL'):
    with it('accepts no-op functions'):
      a = bloom_node.BloomNode()
      a.open('a')  # Needed to trigger visit on `a`.
      visit_fn = mock.Mock(name='visit_fn', __repr__=lambda x: 'visit_fn')
      merge_fn = mock.Mock(name='merge_fn', __repr__=lambda x: 'merge_fn')
      b = a(
          'positional', 'args',
          visit=visit_fn, merge=merge_fn,
          keyword='args'
      )
      expect(repr(b.op)).to(equal(
          "call(BloomNode('', '', 0),"
          " ('positional', 'args'),"
          " {'visit': visit_fn, 'merge': merge_fn, 'keyword': 'args'}"
          ")"
      ))
      expect(repr(b)).to(equal("BloomNode('', '', 0)"))
      expect(visit_fn).to(have_been_called)
      expect(merge_fn).to(have_been_called)

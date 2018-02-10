from data.graph import bloom_node
from spec.mamba import *


with description('construction'):
  with it('constructs without error'):
    expect(calling(bloom_node.BloomNode)).not_to(raise_error)


with description('populating'):
  with before.each:
    self.subject = bloom_node.BloomNode()

  with it('starts out empty'):
    expect(self.subject).to(have_len(0))

  with it('creates if needed'):
    expect(self.subject.open('a')).to(be_a(bloom_node.BloomNode))

  with it('retrieves a created node'):
    a = self.subject.open('a')
    expect(self.subject.open('a')).to(equal(a))

  with description('multi-character'):
    with it('creates if needed'):
      expect(self.subject.open('abc')).to(be_a(bloom_node.BloomNode))

    with it('retrieves a created node'):
      abc = self.subject.open('abc')
      expect(self.subject.open('abc')).to(equal(abc))

  with description('link'):
    with before.each:
      self.child = bloom_node.BloomNode()

    with it('allows a child to be linked'):
      expect(calling(self.subject.link, 'key', self.child)).not_to(raise_error)

    with it('creates a link'):
      self.subject.link('key', self.child)
      expect(self.subject['key']).to(equal(self.child))

    with it('updates masks at root'):
      self.subject.link('a', self.child)
      expect(repr(self.subject)).to(equal("BloomNode('A', '', 0)"))
      self.subject.link('b', self.child)
      expect(repr(self.subject)).to(equal("BloomNode('ab', '', 0)"))
      self.subject.link('c', self.child)
      expect(repr(self.subject)).to(equal("BloomNode('abc', '', 0)"))

    with it('updates masks recursively'):
      cursor = self.child
      cursor.weight(1, True)
      cursor.distance(0)
      for c in 'aba'[::-1]:
        parent = bloom_node.BloomNode()
        parent.link(c, cursor)
        cursor = parent
      expect(repr(cursor)).to(equal("BloomNode('AB', '   #', 0)"))
      expect(repr(cursor['a'])).to(equal("BloomNode('AB', '  #', 0)"))
      expect(repr(cursor['a']['b'])).to(equal("BloomNode('A', ' #', 0)"))
      expect(repr(cursor['a']['b']['a'])).to(equal("BloomNode('', '#', 1)"))

    with it('rejects duplicate links'):
      self.subject.link('key', self.child)
      expect(calling(self.subject.link, 'key', self.child)).to(
          raise_error(KeyError))


with description('api'):
  with before.each:
    self.subject = bloom_node.BloomNode()

  with it('initially empty masks'):
    expect(self.subject.provide_mask).to(equal(0))
    expect(self.subject.require_mask).to(equal(0))
    expect(self.subject.lengths_mask).to(equal(0))

  with it('requires progressively less'):
    self.subject.require(0b111)
    expect(self.subject.require_mask).to(equal(0b111))
    self.subject.require(0b101)
    self.subject.require(0b110)
    expect(self.subject.require_mask).to(equal(0b100))

  with it('provides progressively more'):
    self.subject.require(0b100)
    expect(self.subject.provide_mask).to(equal(0b100))
    self.subject.require(0b101)
    self.subject.require(0b110)
    expect(self.subject.provide_mask).to(equal(0b111))

  with it('iterates over added keys'):
    self.subject.open('first')
    self.subject.open('second')
    expect(set(self.subject)).to(equal({'first', 'second'}))


with description('sources'):
  with before.each:
    def add_node(node: bloom_node.BloomNode, key: str) -> None:
      child = node.open(key)
      child.require(0b111)
      child.distance(0)
      child.weight(1, True)
    self.a = bloom_node.BloomNode()
    add_node(self.a, 'common')  # First bit.
    add_node(self.a, 'a_only')  # Second bit.
    self.b = bloom_node.BloomNode()
    add_node(self.b, 'common')  # First bit.
    add_node(self.b, 'b_only')  # Third bit.
    self.combined = self.a * self.b

  with it('does not find missing nodes'):
    expect(lambda: self.combined['missing']).to(raise_error(KeyError))

  with it('does find common nodes'):
    expect(lambda: self.combined['common']).not_to(raise_error(KeyError))

  with it('propagates common attributes'):
    c = self.combined['common']
    expect(c.provide_mask).to(equal(0b111))
    expect(c.require_mask).to(equal(0b111))
    expect(c.lengths_mask).to(equal(0b1))
    expect(c.match_weight).to(equal(1))

  with it('expands edges when measuring len'):
    expect(self.combined).to(have_len(1))

  with it('expands edges when iterating'):
    expect(set(self.combined)).to(equal({'common'}))

  with it('safely expands remaining edges if one edge was already accessed'):
    expect(self.combined['common']).not_to(be_none)
    expect(calling(repr, self.combined)).not_to(raise_error)


with description('repr') as self:
  with before.each:
    self.subject = bloom_node.BloomNode()

  with it('starts out empty'):
    expect(repr(self.subject)).to(equal("BloomNode('', '', 0)"))

  with it('remembers seen characters and lengths'):
    self.subject.require(0b111)
    self.subject.require(0b101)
    self.subject.distance(3)
    self.subject.distance(2)
    expect(repr(self.subject)).to(equal("BloomNode('AbC', '  ##', 0)"))


with description('annotations'):
  with it('starts empty'):
    node = bloom_node.BloomNode()
    expect(node.annotations()).to(be_empty)

  with it('holds values'):
    node = bloom_node.BloomNode()
    node.annotations({'key': 'value'})
    expect(repr(node)).to(equal("BloomNode('', '', 0, key='value')"))

  with it('merges values via +'):
    a = bloom_node.BloomNode()
    a.annotations({'key': 'value'})
    b = bloom_node.BloomNode()
    node = a + b
    expect(repr(node)).to(equal("BloomNode('', '', 0, key='value')"))

  with it('merges values via *'):
    a = bloom_node.BloomNode()
    a.annotations({'key': 'value'})
    b = bloom_node.BloomNode()
    node = a * b
    expect(repr(node)).to(equal("BloomNode('', '', 0, key='value')"))

  with it('merges duplicates'):
    a = bloom_node.BloomNode()
    a.annotations({'key': 'value1'})
    b = bloom_node.BloomNode()
    b.annotations({'key': 'value2'})
    node = a + b
    expect(repr(node)).to(
        equal("BloomNode('', '', 0, key={'value1', 'value2'})"))

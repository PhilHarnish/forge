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
    self.combined = bloom_node.BloomNode([self.a, self.b])

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


with description('repr'):
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


with description('reduce'):
  with before.each:
    self.a = bloom_node.BloomNode()
    self.a.require(0b111)
    self.a.distance(0)
    self.a.weight(1, True)

  with it('ignores empty input'):
    expect(calling(bloom_node.reduce, [])).not_to(raise_error)

  with it('returns a similar node for one element'):
    outer = bloom_node.reduce([self.a])
    expect(outer.provide_mask).to(equal(self.a.provide_mask))
    expect(outer.require_mask).to(equal(self.a.require_mask))
    expect(outer.lengths_mask).to(equal(self.a.lengths_mask))
    expect(outer.match_weight).to(equal(self.a.match_weight))
    expect(repr(outer)).to(equal(repr(self.a)))

  with it('merges similar nodes'):
    b = bloom_node.BloomNode()
    b.require(0b101)
    b.provide_mask = 0b1111  # Simulate providing more than needing.
    self.a.provide_mask = 0b1111
    b.distance(0)
    b.weight(0.5, True)
    outer = bloom_node.reduce([self.a, b])
    expect(outer.provide_mask).to(equal(0b1111))
    expect(outer.require_mask).to(equal(0b111))
    expect(outer.lengths_mask).to(equal(0b1))
    expect(outer.match_weight).to(equal(0.5))
    expect(repr(outer)).to(equal("BloomNode('ABCd', '#', 0.5)"))

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

with description('api'):
  with before.each:
    self.subject = bloom_node.BloomNode()

  with it('initially empty masks'):
    expect(self.subject.provide_mask).to(be_none)
    expect(self.subject.require_mask).to(be_none)
    expect(self.subject.lengths_mask).to(be_none)

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

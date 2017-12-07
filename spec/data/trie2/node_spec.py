from data.trie2 import node
from spec.mamba import *


with description('construction'):
  with it('constructs without error'):
    expect(calling(node.Node)).not_to(raise_error)

with description('populating'):
  with before.each:
    self.subject = node.Node()

  with it('starts out empty'):
    expect(self.subject).to(have_len(0))

  with it('increases size with each item'):
    expect(self.subject.add('testa', 1))
    expect(self.subject).to(have_len(1))
    expect(self.subject.add('testb', 1))
    expect(self.subject).to(have_len(1))

  with description('validation'):
    with it('raises if duplicates are added'):
      expect(self.subject.add('test', 1))
      expect(calling(self.subject.add, 'test', 1)).to(raise_error(KeyError))

with description('api'):
  with before.each:
    self.subject = node.Node()
    self.subject.add('a', 1)
    self.subject.add('bc', .5)
    self.subject.add('def', .25)

  with it('get returns None if no child is present'):
    expect(self.subject.get('z')).to(equal(None))

  with it('get returns child'):
    expect(self.subject.get('a')).to(be_a(node.Node))

  with it('get returns child, recursively'):
    expect(self.subject.get('b').get('c')).to(be_a(node.Node))

  with it('items returns all children'):
    expect(self.subject.items()).to(have_len(3))

  with it('knows terminal nodes'):
    expect(self.subject.get('b').match_weight()).to(equal(0))
    expect(self.subject.get('b').get('c').match_weight()).to(equal(0.5))

  with it('knows max value in subtrees'):
    expect(self.subject.magnitude()).to(equal(1))
    expect(self.subject.get('d').magnitude()).to(equal(.25))

with description('repr'):
  with before.each:
    self.subject = node.Node()

  with it('starts out empty'):
    expect(repr(self.subject)).to(equal("Node('', '', 0)"))

  with it('remembers seen characters and lengths'):
    self.subject.add('a', 1)
    self.subject.add('bc', 1)
    self.subject.add('def', 1)
    expect(repr(self.subject)).to(equal("Node('abcdef', ' ###', 0)"))

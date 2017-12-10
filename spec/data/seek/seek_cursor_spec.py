from data.seek import base_seek, node, seek_cursor
from spec.mamba import *


with description('construction'):
  with it('constructs without error'):
    expect(calling(seek_cursor.SeekCursor, None, None, None)).not_to(
        raise_error)

with description('api'):
  with before.each:
    root = node.Node()
    root.add('a', 1)
    root.add('ab', .5)
    root.add('abcd', .25)
    self.subject = base_seek.BaseSeek(root).start()

  with it('has children'):
    expect(self.subject.has_children()).to(be_true)

  with it('returns node children'):
    expect(self.subject.children()).to(have_len(1))
    expect(next(iter(self.subject.children()))).to(equal('a'))
    expect(self.subject.children()['a']).to(be_a(node.Node))

  with it('raises KeyError for garbage'):
    expect(calling(self.subject.seek, 'z')).to(raise_error(KeyError))

  with it('returns child'):
    expect(self.subject.seek('a')).to(be_a(seek_cursor.SeekCursor))

  with it('remembers path'):
    n = self.subject.seek('a').seek('b').seek('c').seek('d')
    expect(n.match()).to(equal(('abcd', .25)))

from data.seek import base_seek, node, seek_cursor
from spec.mamba import *


with description('construction'):
  with it('constructs without error'):
    expect(calling(base_seek.BaseSeek, None)).not_to(raise_error)

with description('start'):
  with before.each:
    self.subject = base_seek.BaseSeek(node.Node())

  with it('returns a SeekCursor'):
    expect(self.subject.start()).to(be_a(seek_cursor.SeekCursor))

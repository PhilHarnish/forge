from data.seek import seek_cursor
from spec.mamba import *


with description('construction'):
  with it('constructs without error'):
    expect(calling(seek_cursor.SeekCursor, None, None, None)).not_to(
        raise_error)

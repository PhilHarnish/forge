from puzzle.pdql import pdql
from spec.mamba import *


with description('input'):
  with it('constructs without error'):
    expect(calling(pdql.input)).not_to(raise_error)

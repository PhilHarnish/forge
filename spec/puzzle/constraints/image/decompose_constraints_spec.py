from puzzle.constraints.image import decompose_constraints
from spec.mamba import *


with description('decompose_constraints') as self:
  with it('instantiates without error'):
    expect(calling(decompose_constraints.DecomposeConstraints)).not_to(raise_error)

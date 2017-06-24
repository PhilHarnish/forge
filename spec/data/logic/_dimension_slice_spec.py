from data.logic import _dimension_slice
from spec.mamba import *

with description('_dimension_slice._DimensionSlice'):
  with description('constructor'):
    with it('handles simple input'):
      expect(calling(
          _dimension_slice._DimensionSlice, None, {}
      )).not_to(raise_error)

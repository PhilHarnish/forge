from data.logic import _dimension_factory, _dimension_slice
from spec.mamba import *

with description('_dimension_slice._DimensionSlice'):
  with description('constructor'):
    with it('handles simple input'):
      expect(calling(
          _dimension_slice._DimensionSlice, None, {}
      )).not_to(raise_error)

  with description('resolve'):
    with before.each:
      self.factory = _dimension_factory._DimensionFactory()
      self.subject = _dimension_slice._DimensionSlice(self.factory, {})

    with it('rejects invalid access'):
      expect(lambda: self.subject.foo).to(raise_error(KeyError))
      expect(lambda: self.subject['foo']).to(raise_error(KeyError))

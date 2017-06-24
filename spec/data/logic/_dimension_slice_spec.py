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

    with it('rejects invalid access'):
      self.empty = _dimension_slice._DimensionSlice(self.factory, {})
      expect(lambda: self.empty.foo).to(raise_error(KeyError))
      expect(lambda: self.empty['foo']).to(raise_error(KeyError))

    with it('accepts valid sub-slices'):
      andy, bob = self.factory(name=['andy', 'bob'])
      cherries, dates = self.factory(fruit=['cherries', 'dates'])
      expect(lambda: andy.dates).not_to(raise_error)
      expect(andy.dates).to(be_a(_dimension_slice._DimensionSlice))
      expect(bob.cherries).to(be_a(_dimension_slice._DimensionSlice))
      expect(dates.bob.address()).to(equal({
        'name': 'bob',
        'fruit': 'dates',
      }))
      expect(cherries.andy.address()).to(equal({
        'name': 'andy',
        'fruit': 'cherries',
      }))

    with it('accepts valid sub-slices'):
      andy, = self.factory(name=['andy'])
      cherries, = self.factory(fruit=['cherries'])
      expect(lambda: andy['cherries']).not_to(raise_error)
      expect(andy['cherries']).to(be_a(_dimension_slice._DimensionSlice))
      expect(andy['cherries'].address()).to(equal({
        'name': 'andy',
        'fruit': 'cherries',
      }))

from data.logic import _ast_factory, _dimension_factory, _dimension_slice
from spec.mamba import *

with description('_dimension_slice._DimensionSlice'):
  with before.each:
    self.factory = _dimension_factory._DimensionFactory()

  with description('constructor'):
    with it('handles simple input'):
      expect(calling(
          _dimension_slice._DimensionSlice, None, {}
      )).not_to(raise_error)

  with description('resolve'):
    with it('rejects invalid access'):
      empty = _dimension_slice._DimensionSlice(self.factory, {})
      expect(lambda: empty.foo).to(raise_error(KeyError))
      expect(lambda: empty['foo']).to(raise_error(KeyError))

    with it('rejects redundant access'):
      a, = self.factory(name=['andy'])
      expect(lambda: a.andy).to(raise_error(KeyError))
      expect(lambda: a['andy']).to(raise_error(KeyError))

    with it('accepts valid sub-slices'):
      andy, bob = self.factory(name=['andy', 'bob'])
      cherries, dates = self.factory(fruit=['cherries', 'dates'])
      expect(lambda: andy.dates).not_to(raise_error)
      expect(andy.dates).to(be_a(_dimension_slice._DimensionSlice))
      expect(bob.cherries).to(be_a(_dimension_slice._DimensionSlice))
      expect(dates.bob.dimension_address()).to(equal({
        'name': 'bob',
        'fruit': 'dates',
      }))
      expect(cherries.andy.dimension_address()).to(equal({
        'name': 'andy',
        'fruit': 'cherries',
      }))

    with it('accepts valid array sub-slices'):
      andy, = self.factory(name=['andy'])
      cherries, = self.factory(fruit=['cherries'])
      expect(lambda: andy['cherries']).not_to(raise_error)
      expect(andy['cherries']).to(be_a(_dimension_slice._DimensionSlice))
      expect(andy['cherries'].dimension_address()).to(equal({
        'name': 'andy',
        'fruit': 'cherries',
      }))
      expect(cherries['andy'].dimension_address()).to(equal({
        'name': 'andy',
        'fruit': 'cherries',
      }))

    with it('accepts slicing dimensions'):
      andy, = self.factory(name=['andy'])
      cherries, = self.factory(fruit=['cherries'])
      expect(lambda: andy.fruit).not_to(raise_error)
      expect(andy.fruit).to(be_a(_dimension_slice._DimensionSlice))
      expect(cherries['name'].dimension_address()).to(equal({
        'name': None,
        'fruit': 'cherries',
      }))

  with description('dimension_name'):
    with it('produces fully qualified names'):
      andy, = self.factory(name=['andy'])
      cherries, = self.factory(fruit=['cherries'])
      expect(andy.cherries.dimension_address_name()).to(
          equal('name["andy"].fruit["cherries"]'))
      expect(cherries.andy.dimension_address_name()).to(
          equal('name["andy"].fruit["cherries"]'))

  with description('cache'):
    with it('returns unique slices for new requests'):
      andy, bob = self.factory(name=['andy', 'bob'])
      cherries, dates = self.factory(fruit=['cherries', 'dates'])
      slices = [
        andy.fruit, andy.cherries, andy.dates,
        bob.fruit, bob.cherries, bob.dates,
        cherries.name, cherries.andy, cherries.bob,
        dates.name, dates.andy, dates.bob,
      ]
      seen = set()
      for slice in slices:
        address = id(slice)
        expect(seen).not_to(contain(address))

    with it('returns cached slices for repeated requests'):
      andy, = self.factory(name=['andy'])
      cherries, = self.factory(fruit=['cherries'])
      expect(andy.cherries).to(be(andy['cherries']))
      expect(andy.fruit).to(be(andy['fruit']))
      expect(cherries.andy).to(be(cherries['andy']))
      expect(cherries.name).to(be(cherries['name']))

  with description('operators'):
    with description('eq'):
      with it('accepts two unconstrained slices'):
        andy, = self.factory(name=['andy'])
        cherries, = self.factory(fruit=['cherries'])
        expression = andy == cherries
        expect(expression).to(be_a(_ast_factory.AccumulatingExpr))

      with it('accumulates comparisons'):
        andy, bob = self.factory(name=['andy', 'bob'])
        age = self.factory(age=[10, 11])
        expression = ((andy.age + 1) == bob)
        expect(expression).to(be_a(_ast_factory.AccumulatingExpr))

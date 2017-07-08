from data.logic import _dimension_factory, _dimension_slice
from spec.mamba import *

with description('_dimension_factory._DimensionFactory'):
  with before.each:
    self.subject = _dimension_factory._DimensionFactory()

  with description('constructor'):
    with it('handles empty input'):
      expect(calling(self.subject)).to(raise_error)

    with it('handles kwargs'):
      expect(calling(self.subject, name=['A'])).not_to(raise_error)

    with it('rejects multiple kwargs'):
      expect(calling(self.subject, name=['A'], age=[1])).to(raise_error)

  with description('registering'):
    with it('remembers registered dimensions'):
      self.subject(name=['A', 'B'])
      dimensions = self.subject.dimensions()
      expect(dimensions).to(have_key('name'))
      for dimension in dimensions.values():
        expect(dimension).to(have_len(2))
        for slice in dimension.values():
          expect(slice).to(be_a(_dimension_slice._DimensionSlice))

    with it('prevents duplicate dimension registration'):
      self.subject(name=['A', 'B'])
      expect(calling(self.subject, name=['A', 'B'])).to(raise_error(TypeError))

    with it('allows duplicate value registration'):
      expect(calling(self.subject, name=['A', 'B', 'B'])).not_to(raise_error)

  with description('value_cardinality'):
    with it('returns value cardinality for registered values'):
      self.subject(name=['A', 'B', 'B'])
      expect(self.subject.value_cardinality('A')).to(equal(1))
      expect(self.subject.value_cardinality('B')).to(equal(2))

  with description('cardinality groups'):
    with it('returns 2D rows and columns'):
      self.subject(name=['A', 'B'])
      self.subject(number=[1, 2])
      groups = self.subject.cardinality_groups()
      expect(groups).to(equal([
        # Row A.
        ([{'name': 'A', 'number': 1}, {'name': 'A', 'number': 2}], 1),
        # Row B.
        ([{'name': 'B', 'number': 1}, {'name': 'B', 'number': 2}], 1),
        # Column 1.
        ([{'name': 'A', 'number': 1}, {'name': 'B', 'number': 1}], 1),
        # Column 2.
        ([{'name': 'A', 'number': 2}, {'name': 'B', 'number': 2}], 1),
      ]))

    with it('returns 2D rows and columns with duplicates'):
      self.subject(name=['A', 'B'])
      self.subject(number=[1, 1])
      groups = self.subject.cardinality_groups()
      expect(groups).to(equal([
        # Only one value, cardinality is one.
        ([{'name': 'A', 'number': 1}], 1),
        ([{'name': 'B', 'number': 1}], 1),
        # Both A and B will be 1, cardinality is 2.
        ([{'name': 'A', 'number': 1}, {'name': 'B', 'number': 1}], 2)
      ]))

    with it('returns 3D rows and columns'):
      self.subject(name=['A', 'B'])
      self.subject(number=[1, 2])
      self.subject(another=['x', 'y'])
      groups = self.subject.cardinality_groups()
      expect(groups).to(have_len(2 * 2 * 3))
      expect(groups[4 * 0][0]).to(equal([
        # Row A + number.
        {'name': 'A', 'number': 1}, {'name': 'A', 'number': 2}
      ]))
      expect(groups[4 * 1][0]).to(equal([
        # Row A + another.
        {'name': 'A', 'another': 'x'}, {'name': 'A', 'another': 'y'}
      ]))
      expect(groups[4 * 2][0]).to(equal([
        # Row number 1 + another.
        {'number': 1, 'another': 'x'}, {'number': 1, 'another': 'y'}
      ]))

  with description('resolve'):
    with it('resolves subslice dimensions'):
      self.subject(name=['a', 'b'])
      slice = _dimension_slice._DimensionSlice(self, {})
      resolved = self.subject.resolve(slice, 'name')
      expect(resolved).to(be_a(_dimension_slice._DimensionSlice))
      expect(resolved.dimension_constraints()).to(equal({'name': None}))

    with it('resolves subslice values'):
      self.subject(name=['a', 'b'])
      slice = _dimension_slice._DimensionSlice(self, {})
      resolved = self.subject.resolve(slice, 'a')
      expect(resolved).to(be_a(_dimension_slice._DimensionSlice))
      expect(resolved.dimension_constraints()).to(equal({'name': 'a'}))

    with it('resolves subslices iteravely'):
      self.subject(name=['a', 'b'])
      self.subject(age=[10, 11])
      slice = _dimension_slice._DimensionSlice(self, {})
      resolved = self.subject.resolve(slice, 'a')
      resolved = self.subject.resolve(resolved, 11)
      expect(resolved).to(be_a(_dimension_slice._DimensionSlice))
      expect(resolved.dimension_constraints()).to(equal({
        'name': 'a',
        'age': 11,
      }))

    with it('resolves literal values when requested'):
      age = self.subject(age=[10, 11])
      expect(age[10].age).to(equal(10))

  with description('resolve_all'):
    with it('returns 1 slice for fixed dimension slices'):
      self.subject(name=['a', 'b'])
      slice = _dimension_slice._DimensionSlice(self, {'name': 'a'})
      expect(self.subject.resolve_all(slice)).to(equal([slice]))

    with it('returns all unconstrained sub-slices'):
      self.subject(name=['a', 'b'])
      slice = _dimension_slice._DimensionSlice(self, {'name': None})
      expect(list(map(str, self.subject.resolve_all(slice)))).to(equal([
        'name["a"]', 'name["b"]'
      ]))

  with description('inference groups'):
    with it('returns nothing for 2 dimensions'):
      self.subject(name=['A', 'B'])
      self.subject(number=[1, 2])
      groups = self.subject.inference_groups()
      expect(groups).to(equal([]))

    with it('returns results for 3 dimensions'):
      self.subject(a=['A', 'B'])
      self.subject(b=[1, 1])
      self.subject(c=['x', 'y'])
      groups = self.subject.inference_groups()
      expect(groups).to(equal([
        (({'a': 'A', 'b': 1}, 2), ({'a': 'A', 'c': 'x'}, 1), (
          {'c': 'x', 'b': 1}, 2)),
        (({'a': 'A', 'b': 1}, 2), ({'a': 'A', 'c': 'y'}, 1), (
          {'c': 'y', 'b': 1}, 2)),
        (({'a': 'B', 'b': 1}, 2), ({'a': 'B', 'c': 'x'}, 1), (
          {'c': 'x', 'b': 1}, 2)),
        (({'a': 'B', 'b': 1}, 2), ({'a': 'B', 'c': 'y'}, 1), (
          {'c': 'y', 'b': 1}, 2)),
      ]))

  with description('unpacking'):
    with it('raises on empty input'):
      def bad():
        (_,) = self.subject()


      expect(calling(bad)).to(raise_error)

    with it('unpacks matched lengths'):
      def good():
        (_, _) = self.subject(key=['A', 'B'])


      expect(good).not_to(raise_error)

    with it('unpacks matched lengths with repeats'):
      def good():
        (_, _, _) = self.subject(key=['A', 'B', 'B'])


      expect(good).not_to(raise_error)

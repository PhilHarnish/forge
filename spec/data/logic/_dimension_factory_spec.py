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
        ([{'number': None, 'name': 'A'}, {'number': None, 'name': 'B'}], 0)
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

    with it('returns 2D rows and columns with different sizes'):
      self.subject(name=['A', 'B', 'C'])
      self.subject(number=[5, 6])
      groups = self.subject.cardinality_groups()
      expect(groups).to(equal([
        ([{'name': 'A', 'number': 5}, {'name': 'A', 'number': 6}], 1),
        ([{'name': 'B', 'number': 5}, {'name': 'B', 'number': 6}], 1),
        ([{'name': 'C', 'number': 5}, {'name': 'C', 'number': 6}], 1),
      ]))

    with it('returns 3D rows and columns'):
      self.subject(a=['A', 'B'])
      self.subject(b=[1, 2])
      self.subject(c=['x', 'y'])
      groups = self.subject.cardinality_groups()
      expect(groups).to(equal([
        ([{'b': None, 'a': 'A'}, {'b': None, 'a': 'B'}], 0),
        ([{'a': 'A', 'c': 'x'}, {'a': 'A', 'c': 'y'}], 1),
        ([{'a': 'B', 'c': 'x'}, {'a': 'B', 'c': 'y'}], 1),
        ([{'a': 'A', 'c': 'x'}, {'a': 'B', 'c': 'x'}], 1),
        ([{'a': 'A', 'c': 'y'}, {'a': 'B', 'c': 'y'}], 1),
        ([{'b': None, 'c': 'x'}, {'b': None, 'c': 'y'}], 0),
      ]))

    with it('returns 3D rows and columns with different sizes'):
      self.subject(d1=['A', 'B', 'C', 'D'])
      self.subject(d2=[1, 2, 3])
      self.subject(d3=['x', 'y'])
      groups = self.subject.cardinality_groups()
      expect(groups).to(equal([
        ([{'d1': 'A', 'd2': 1}, {'d1': 'A', 'd2': 2}, {'d1': 'A', 'd2': 3}], 1),
        ([{'d1': 'B', 'd2': 1}, {'d1': 'B', 'd2': 2}, {'d1': 'B', 'd2': 3}], 1),
        ([{'d1': 'C', 'd2': 1}, {'d1': 'C', 'd2': 2}, {'d1': 'C', 'd2': 3}], 1),
        ([{'d1': 'D', 'd2': 1}, {'d1': 'D', 'd2': 2}, {'d1': 'D', 'd2': 3}], 1),
        ([{'d1': 'A', 'd3': 'x'}, {'d1': 'A', 'd3': 'y'}], 1),
        ([{'d1': 'B', 'd3': 'x'}, {'d1': 'B', 'd3': 'y'}], 1),
        ([{'d1': 'C', 'd3': 'x'}, {'d1': 'C', 'd3': 'y'}], 1),
        ([{'d1': 'D', 'd3': 'x'}, {'d1': 'D', 'd3': 'y'}], 1),
        ([{'d2': 1, 'd3': 'x'}, {'d2': 1, 'd3': 'y'}], 2),
        ([{'d2': 2, 'd3': 'x'}, {'d2': 2, 'd3': 'y'}], 2),
        ([{'d2': 3, 'd3': 'x'}, {'d2': 3, 'd3': 'y'}], 2),
      ]))

  with description('inference groups'):
    with it('returns nothing for 2 dimensions'):
      self.subject(name=['A', 'B'])
      self.subject(number=[1, 2])
      groups = self.subject.inference_groups()
      expect(groups).to(equal([]))

    with it('returns results for 3 dimensions with duplicates'):
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

    with it('returns results for 3 dimensions with uneven sizes'):
      self.subject(a=['A', 'B', 'C'])
      self.subject(b=['x'])
      self.subject(c=['y'])
      groups = self.subject.inference_groups()
      expect(groups).to(equal([
        (({'a': 'A', 'b': 'x'}, 3), ({'a': 'A', 'c': 'y'}, 3), (
          {'b': 'x', 'c': 'y'}, 9)),
        (({'a': 'B', 'b': 'x'}, 3), ({'a': 'B', 'c': 'y'}, 3), (
          {'b': 'x', 'c': 'y'}, 9)),
        (({'a': 'C', 'b': 'x'}, 3), ({'a': 'C', 'c': 'y'}, 3), (
          {'b': 'x', 'c': 'y'}, 9))
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

    with it('resolves subslice using another dimension slice'):
      self.subject(name=['a', 'b'])
      slice1 = _dimension_slice._DimensionSlice(self, {})
      slice2 = _dimension_slice._DimensionSlice(self, {'name': 'a'})
      resolved = self.subject.resolve(slice1, slice2)
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

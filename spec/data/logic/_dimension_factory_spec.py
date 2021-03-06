from data.logic import _dimension_factory, _dimension_slice
from spec.mamba import *

with description('_dimension_factory._DimensionFactory'):
  with before.each:
    self.subject = _dimension_factory._DimensionFactory()

  with description('constructor'):
    with it('rejects empty input'):
      expect(calling(self.subject)).to(raise_error)

    with it('accepts args'):
      expect(calling(self.subject, ('name', ['A']))).not_to(raise_error)

    with it('accepts multiple args'):
      expect(calling(self.subject, ('name', ['A']), ('age', [1]))).not_to(
          raise_error)

    with it('accepts args with dimension counts'):
      expect(calling(self.subject, ('name', 2, ['A', 'B']))).not_to(raise_error)

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

    with it('supports cross-product dimensions'):
      self.subject(
          ('room', ['A', 'B']),
          ('floor', [1, 2]),
          ('side', ['L', 'R']),
      )
      dimensions = self.subject.dimensions()
      expect(dimensions).to(have_key('room_floor_side'))
      expect(list(dimensions['room_floor_side'].keys())).to(equal(
          ['A1L', 'A1R', 'A2L', 'A2R', 'B1L', 'B1R', 'B2L', 'B2R']))

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
      groups = self.subject._append_cardinality_groups()
      expect(groups).to(equal([
        _dimension_factory.UniqueCardinality(group=[
          {'number': None, 'name': 'A'}, {'number': None, 'name': 'B'}
        ])
      ]))

    with it('returns 2D rows and columns with duplicates'):
      self.subject(name=['A', 'B'])
      self.subject(number=[1, 1])
      groups = self.subject._append_cardinality_groups()
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
      groups = self.subject._append_cardinality_groups()
      expect(groups).to(equal([
        _dimension_factory.Cardinality(group=[
          {'name': 'A', 'number': 5}, {'name': 'A', 'number': 6}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'name': 'B', 'number': 5}, {'name': 'B', 'number': 6}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'name': 'C', 'number': 5}, {'name': 'C', 'number': 6}
        ], cardinality=1),
        _dimension_factory.CardinalityRange(group=[
          {'number': 5, 'name': 'A'}, {'number': 5, 'name': 'B'},
          {'number': 5, 'name': 'C'}
        ], min_cardinality=1, max_cardinality=2),
        _dimension_factory.CardinalityRange(group=[
          {'number': 6, 'name': 'A'}, {'number': 6, 'name': 'B'},
          {'number': 6, 'name': 'C'}
        ], min_cardinality=1, max_cardinality=2)
      ]))

    with it('returns 2D rows and columns with different number of duplicates'):
      # 2-3 of each of these.
      self.subject(dupes=[3, 3, 2, 2, 2, 1, 1])
      # Only 1 "B".
      self.subject(one=['A', 'A', 'A', 'A', 'A', 'A', 'B'])
      groups = self.subject._append_cardinality_groups()
      expect(groups).to(equal([
        _dimension_factory.Cardinality(group=[
          {'dupes': 3, 'one': 'A'}, {'dupes': 3, 'one': 'B'}
        ], cardinality=2),
        _dimension_factory.Cardinality(group=[
          {'dupes': 2, 'one': 'A'}, {'dupes': 2, 'one': 'B'}
        ], cardinality=3),
        _dimension_factory.Cardinality(group=[
          {'dupes': 1, 'one': 'A'}, {'dupes': 1, 'one': 'B'}
        ], cardinality=2),
        _dimension_factory.Cardinality(group=[
          {'one': 'A', 'dupes': 3}, {'one': 'A', 'dupes': 2},
          {'one': 'A', 'dupes': 1}
        ], cardinality=6),
        _dimension_factory.Cardinality(group=[
          {'one': 'B', 'dupes': 3}, {'one': 'B', 'dupes': 2},
          {'one': 'B', 'dupes': 1}
        ], cardinality=1)]))

    with it('returns 2D rows and columns with different counts'):
      # 2-3 of each of these.
      self.subject(['a', 3, ['x', 'y']])
      # Only 1 "B".
      self.subject(['b', ['q', 'r']])
      groups = self.subject._append_cardinality_groups()
      expect(groups).to(equal([
        _dimension_factory.Cardinality(group=[
          # a: x.
          {'a': 'x', 'b': 'q'}, {'a': 'x', 'b': 'r'}
        ], cardinality=3),
        _dimension_factory.Cardinality(group=[
          # a: y.
          {'a': 'y', 'b': 'q'}, {'a': 'y', 'b': 'r'}
        ], cardinality=3),
        _dimension_factory.CardinalityRange(group=[
          {'b': 'q', 'a': 'x'}, {'b': 'q', 'a': 'y'}
        ], min_cardinality=1, max_cardinality=6),
        _dimension_factory.CardinalityRange(group=[
          {'b': 'r', 'a': 'x'}, {'b': 'r', 'a': 'y'}
        ], min_cardinality=1, max_cardinality=6)
      ]))

    with it('returns 3D rows and columns'):
      self.subject(a=['A', 'B'])
      self.subject(b=[1, 2])
      self.subject(c=['x', 'y'])
      groups = self.subject._append_cardinality_groups()
      expect(groups).to(equal([
        _dimension_factory.UniqueCardinality(group=[
          {'b': None, 'a': 'A'}, {'b': None, 'a': 'B'}
        ]),
        _dimension_factory.Cardinality(group=[
          {'a': 'A', 'c': 'x'}, {'a': 'A', 'c': 'y'}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'a': 'B', 'c': 'x'}, {'a': 'B', 'c': 'y'}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'c': 'x', 'a': 'A'}, {'c': 'x', 'a': 'B'}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'c': 'y', 'a': 'A'}, {'c': 'y', 'a': 'B'}
        ], cardinality=1),
        _dimension_factory.UniqueCardinality(group=[
          {'b': None, 'c': 'x'}, {'b': None, 'c': 'y'}
        ])
      ]))

    with it('returns 3D rows and columns with different sizes'):
      self.subject(d1=['A', 'B', 'C', 'D'])
      self.subject(d2=[1, 2, 3])
      self.subject(d3=['x', 'y'])
      groups = self.subject._append_cardinality_groups()
      expect(groups).to(equal([
        _dimension_factory.Cardinality(group=[
          {'d1': 'A', 'd2': 1}, {'d1': 'A', 'd2': 2}, {'d1': 'A', 'd2': 3}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'d1': 'B', 'd2': 1}, {'d1': 'B', 'd2': 2}, {'d1': 'B', 'd2': 3}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'d1': 'C', 'd2': 1}, {'d1': 'C', 'd2': 2}, {'d1': 'C', 'd2': 3}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'d1': 'D', 'd2': 1}, {'d1': 'D', 'd2': 2}, {'d1': 'D', 'd2': 3}
        ], cardinality=1),
        _dimension_factory.CardinalityRange(group=[
          {'d2': 1, 'd1': 'A'}, {'d2': 1, 'd1': 'B'}, {'d2': 1, 'd1': 'C'},
          {'d2': 1, 'd1': 'D'}
        ], min_cardinality=1, max_cardinality=2),
        _dimension_factory.CardinalityRange(group=[
          {'d2': 2, 'd1': 'A'}, {'d2': 2, 'd1': 'B'}, {'d2': 2, 'd1': 'C'},
          {'d2': 2, 'd1': 'D'}
        ], min_cardinality=1, max_cardinality=2),
        _dimension_factory.CardinalityRange(group=[
          {'d2': 3, 'd1': 'A'}, {'d2': 3, 'd1': 'B'}, {'d2': 3, 'd1': 'C'},
          {'d2': 3, 'd1': 'D'}
        ], min_cardinality=1, max_cardinality=2),
        _dimension_factory.Cardinality(group=[
          {'d1': 'A', 'd3': 'x'}, {'d1': 'A', 'd3': 'y'}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'d1': 'B', 'd3': 'x'}, {'d1': 'B', 'd3': 'y'}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'d1': 'C', 'd3': 'x'}, {'d1': 'C', 'd3': 'y'}
        ], cardinality=1),
        _dimension_factory.Cardinality(group=[
          {'d1': 'D', 'd3': 'x'}, {'d1': 'D', 'd3': 'y'}
        ], cardinality=1),
        _dimension_factory.CardinalityRange(group=[
          {'d3': 'x', 'd1': 'A'}, {'d3': 'x', 'd1': 'B'},
          {'d3': 'x', 'd1': 'C'}, {'d3': 'x', 'd1': 'D'}
        ], min_cardinality=1, max_cardinality=3),
        _dimension_factory.CardinalityRange(group=[
          {'d3': 'y', 'd1': 'A'}, {'d3': 'y', 'd1': 'B'},
          {'d3': 'y', 'd1': 'C'}, {'d3': 'y', 'd1': 'D'}
        ], min_cardinality=1, max_cardinality=3),
        _dimension_factory.CardinalityRange(group=[
          {'d2': 1, 'd3': 'x'}, {'d2': 1, 'd3': 'y'}
        ], min_cardinality=1, max_cardinality=2),
        _dimension_factory.CardinalityRange(group=[
          {'d2': 2, 'd3': 'x'}, {'d2': 2, 'd3': 'y'}
        ], min_cardinality=1, max_cardinality=2),
        _dimension_factory.CardinalityRange(group=[
          {'d2': 3, 'd3': 'x'}, {'d2': 3, 'd3': 'y'}
        ], min_cardinality=1, max_cardinality=2),
        _dimension_factory.CardinalityRange(group=[
          {'d3': 'x', 'd2': 1}, {'d3': 'x', 'd2': 2}, {'d3': 'x', 'd2': 3}
        ], min_cardinality=1, max_cardinality=3),
        _dimension_factory.CardinalityRange(group=[
          {'d3': 'y', 'd2': 1}, {'d3': 'y', 'd2': 2}, {'d3': 'y', 'd2': 3}
        ], min_cardinality=1, max_cardinality=3)
      ]))

  with description('inference groups'):
    with it('returns nothing for 2 dimensions'):
      self.subject(name=['A', 'B'])
      self.subject(number=[1, 2])
      groups = self.subject._append_inference_groups()
      expect(groups).to(equal([]))

    with it('returns results for 3 dimensions with duplicates'):
      self.subject(a=['A', 'B'])
      self.subject(b=[1, 1])
      self.subject(c=['x', 'y'])
      groups = self.subject._append_inference_groups()
      expect(groups).to(equal([
        _dimension_factory.Inference(group=[
          {'a': 'A', 'c': 'x'}, {'a': 'A', 'b': 1}, {'b': 1, 'c': 'x'}
        ], cardinalities=[1, 2, 2]),
        _dimension_factory.Inference(group=[
          {'a': 'A', 'c': 'y'}, {'a': 'A', 'b': 1}, {'b': 1, 'c': 'y'}
        ], cardinalities=[1, 2, 2]),
        _dimension_factory.Inference(group=[
          {'a': 'B', 'c': 'x'}, {'a': 'B', 'b': 1}, {'b': 1, 'c': 'x'}
        ], cardinalities=[1, 2, 2]),
        _dimension_factory.Inference(group=[
          {'a': 'B', 'c': 'y'}, {'a': 'B', 'b': 1}, {'b': 1, 'c': 'y'}
        ], cardinalities=[1, 2, 2])
      ]))

    with it('returns results for 3 dimensions with uneven sizes'):
      self.subject(a=['A', 'B', 'C'])
      self.subject(b=['x'])
      self.subject(c=['y'])
      groups = self.subject._append_inference_groups()
      expect(groups).to(equal([
        _dimension_factory.Inference(group=[
          {'a': 'A', 'b': 'x'}, {'a': 'A', 'c': 'y'}, {'b': 'x', 'c': 'y'}
        ], cardinalities=[3, 3, 9]),
        _dimension_factory.Inference(group=[
          {'a': 'B', 'b': 'x'}, {'a': 'B', 'c': 'y'}, {'b': 'x', 'c': 'y'}
        ], cardinalities=[3, 3, 9]),
        _dimension_factory.Inference(group=[
          {'a': 'C', 'b': 'x'}, {'a': 'C', 'c': 'y'}, {'b': 'x', 'c': 'y'}
        ], cardinalities=[3, 3, 9])
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

    with it('unpacks cross-product dimensions'):
      def good():
        _ = (_, _, _) = ((_, _, _, _, _, _, _, _), _, _) = self.subject(
          ('room', ['A', 'B']),
          ('floor', [1, 2]),
          ('side', ['L', 'R']),
        )


      expect(good).not_to(raise_error)

    with it('unpacked cross-product dimensions are also correct'):
      room_floor_side = (room, floor, side) = ((
        A1N, A1S, A1E, A1W,
        A2N, A2S, A2E, A2W,
        A3N, A3S, A3E, A3W,
        B1N, B1S, B1E, B1W,
        B2N, B2S, B2E, B2W,
        B3N, B3S, B3E, B3W,
      ), _, _) = self.subject(
        ('room', ['A', 'B']),
        ('floor', [1, 2, 3]),
        ('direction', ['N', 'S', 'E', 'W']),
      )
      expect(list(room)).to(have_len(2 * 3 * 4))
      for r in room:
        expect(r).to(be_a(_dimension_slice._DimensionSlice))

    with it('unpacked cross-product dimensions can be sub-sliced'):
      (room, _, _) = self.subject(
        ('room', ['A', 'B']),
        ('floor', [1, 2, 3]),
        ('direction', ['N', 'S', 'E', 'W']),
      )
      expect(list(room['A'])).to(have_len(3 * 4))
      for r in room['A']:
        constraints = r.dimension_constraints()
        expect(constraints).to(have_key('room_floor_direction'))
        expect(constraints['room_floor_direction']).to(contain('A'))
      expect(list(room['A'][1])).to(have_len(4))
      for r in room['A'][1]:
        constraints = r.dimension_constraints()
        expect(constraints).to(have_key('room_floor_direction'))
        expect(constraints['room_floor_direction']).to(contain('A1'))

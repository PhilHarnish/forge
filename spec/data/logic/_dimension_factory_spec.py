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

    with it('prevents duplicate registration'):
      self.subject(name=['A', 'B'])
      expect(calling(self.subject, name=['A', 'B'])).to(raise_error(TypeError))

  with description('cardinality groups'):
    with it('returns 2D rows and columns'):
      self.subject(name=['A', 'B'])
      self.subject(number=[1, 2])
      groups = self.subject.cardinality_groups()
      expect(groups).to(equal([
        # Row A.
        [{'name': 'A', 'number': 1}, {'name': 'A', 'number': 2}],
        # Row B.
        [{'name': 'B', 'number': 1}, {'name': 'B', 'number': 2}],
        # Column 1.
        [{'name': 'A', 'number': 1}, {'name': 'B', 'number': 1}],
        # Column 2.
        [{'name': 'A', 'number': 2}, {'name': 'B', 'number': 2}]
      ]))

    with it('returns 3D rows and columns'):
      self.subject(name=['A', 'B'])
      self.subject(number=[1, 2])
      self.subject(another=['x', 'y'])
      groups = self.subject.cardinality_groups()
      expect(groups).to(have_len(2 * 2 * 3))
      expect(groups[4 * 0]).to(equal([
        # Row A + number.
        {'name': 'A', 'number': 1}, {'name': 'A', 'number': 2}
      ]))
      expect(groups[4 * 1]).to(equal([
        # Row A + another.
        {'name': 'A', 'another': 'x'}, {'name': 'A', 'another': 'y'}
      ]))
      expect(groups[4 * 2]).to(equal([
        # Row number 1 + another.
        {'number': 1, 'another': 'x'}, {'number': 1, 'another': 'y'}
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

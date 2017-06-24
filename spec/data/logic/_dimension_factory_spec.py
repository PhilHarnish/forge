from data.logic import _dimension_factory
from spec.mamba import *

_DIMENSIONS_OUT = """
   (Andy, Bob, Cathy) = dimensions(name=['Andy', 'Bob', 'Cathy'])
"""

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
      expect(self.subject._dimensions).to(equal({
        'name': ['A', 'B'],
      }))

    with it('prevents duplicate registration'):
      self.subject(name=['A', 'B'])
      expect(calling(self.subject, name=['A', 'B'])).to(raise_error(TypeError))

  with description('unpacking'):
    with it('raises on empty input'):
      def bad():
        (ex,) = self.subject()


      expect(calling(bad)).to(raise_error)

    with it('unpacks matched lengths'):
      def good():
        (a, b) = self.subject(key=['A', 'B'])


      expect(good).not_to(raise_error)

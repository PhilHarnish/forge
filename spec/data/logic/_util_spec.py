from data.logic import _util
from spec.mamba import *

with description('_util'):
  with description('address'):
    with before.each:
      self.dimensions = ['name', 'fruit', 'age']

    with it('accepts empty input'):
      expect(_util.address(self.dimensions, {})).to(equal(''))

    with it('accepts simple input'):
      expect(_util.address(self.dimensions, {'name': None})).to(equal(
          'name[None]'))

    with it('accepts varied input'):
      expect(_util.address(self.dimensions, {
        'name': None,
        'age': 1,
        'fruit': 'apple',
      })).to(equal('name[None].fruit["apple"].age[1]'))

  with description('parse'):
    with it('handles simple input'):
      expect(_util.parse('var_a["key_a"]')).to(equal({'var_a': 'key_a'}))

    with it('handles compound input'):
      expect(_util.parse('var_a["key_a"].var_b["key_b"]')).to(equal({
        'var_a': 'key_a',
        'var_b': 'key_b',
      }))

    with it('handles primitives'):
      expect(_util.parse('var_a[None]')).to(equal({'var_a': None}))
      expect(_util.parse('var_a[1]')).to(equal({'var_a': 1}))

  with description('combine'):
    with it('combines empty objects'):
      expect(_util.combine({}, {})).to(equal({}))

    with it('merges objects with None'):
      expect(_util.combine({'a': None}, {'a': 1})).to(equal({'a': 1}))
      expect(_util.combine({'a': 1}, {'a': None})).to(equal({'a': 1}))

    with it('merges non-overlapping dimensions'):
      expect(_util.combine({'a': 1}, {'b': 2})).to(equal({'a': 1, 'b': 2}))

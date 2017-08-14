import ast

import Numberjack

from data.logic import _util
from spec.mamba import *

with description('_util'):
  with description('address'):
    with before.each:
      self.dimensions = ['name', 'fruit', 'age']

    with it('accepts empty input'):
      expect(_util.address(self.dimensions, {})).to(equal(''))

    with it('accepts simple input'):
      expect(_util.address(self.dimensions, {'name': None})).to(equal('name'))

    with it('accepts varied input'):
      expect(_util.address(self.dimensions, {
        'name': None,
        'age': 1,
        'fruit': 'apple',
      })).to(equal('name.fruit["apple"].age[1]'))

  with description('parse'):
    with it('handles simple input'):
      expect(_util.parse('var_a["key_a"]')).to(equal({'var_a': 'key_a'}))

    with it('handles compound input'):
      expect(_util.parse('var_a["key_a"].var_b["key_b"]')).to(equal({
        'var_a': 'key_a',
        'var_b': 'key_b',
      }))

    with it('handles primitives'):
      expect(_util.parse('var_a')).to(equal({'var_a': None}))
      expect(_util.parse('var_a[1]')).to(equal({'var_a': 1}))

  with description('combine'):
    with it('combines empty objects'):
      expect(_util.combine({}, {})).to(equal({}))

    with it('merges objects with None'):
      expect(_util.combine({'a': None}, {'a': 1})).to(equal({'a': 1}))
      expect(_util.combine({'a': 1}, {'a': None})).to(equal({'a': 1}))

    with it('merges non-overlapping dimensions'):
      expect(_util.combine({'a': 1}, {'b': 2})).to(equal({'a': 1, 'b': 2}))

    with it('rejects duplicates'):
      expect(calling(_util.combine, {'a': 1}, {'a': 2})).to(
          raise_error(KeyError))

  with description('numberjack_solution'):
    with before.each:
      self.a = Numberjack.Variable('a')
      self.b = Numberjack.Variable('b')
      self.c = Numberjack.Variable('c')
      self.model = Numberjack.Model()
      self.solve = lambda: self.model.load('Mistral').solve()

    with it('raises if unsolved'):
      expect(calling(_util.numberjack_solution, self.a)).to(
          raise_error(ValueError))

    with it('raises if given garbage input'):
      expect(calling(_util.numberjack_solution, None)).to(
          raise_error(TypeError))

    with it('returns primitives'):
      expect(calling(_util.numberjack_solution, True)).to(equal(True))
      expect(calling(_util.numberjack_solution, 1)).to(equal(1))
      expect(calling(_util.numberjack_solution, 'asdf')).to(equal('asdf'))

    with it('returns solutions'):
      self.model.add(self.a == self.b)
      self.model.add(self.b == True)
      self.solve()
      expect(calling(_util.numberjack_solution, self.a)).to(equal(True))

    with it('returns compound expressions'):
      self.model.add(self.a + self.b + self.c == 3)
      self.solve()
      expect(calling(_util.numberjack_solution, self.a)).to(equal(True))

    with it('returns intermediate fn expressions'):
      intermediate1 = Numberjack.Sum([self.a, self.b, self.c], [1, 2, 3])
      intermediate2 = Numberjack.Abs(intermediate1 - 10)
      self.model.add(intermediate2 == 4)
      self.solve()
      expect(intermediate1.is_built()).to(be_false)
      expect(calling(_util.numberjack_solution, intermediate1)).to(equal(6))

with description('literal_value'):
  with before.each:
    self.node = lambda v: ast.parse(repr(v)).body[0].value

  with it('handles constants'):
    examples = [None, True, False]
    for example in examples:
      expect(call(_util.literal_value, self.node(example))).to(equal(example))

  with it('handles strings'):
    examples = ['', 'asdf']
    for example in examples:
      expect(call(_util.literal_value, self.node(example))).to(equal(example))

  with it('handles numbers'):
    examples = [0, 1, 1.1]
    for example in examples:
      expect(call(_util.literal_value, self.node(example))).to(equal(example))

  with it('handles lists'):
    examples = [[], [1], [1, False]]
    for example in examples:
      expect(call(_util.literal_value, self.node(example))).to(equal(example))

  with it('handles tuples'):
    examples = [(), (1,), (1, False)]
    for example in examples:
      expect(call(_util.literal_value, self.node(example))).to(equal(example))

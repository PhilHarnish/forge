import re

from data.logic import _dimension_factory, _model, _reference
from spec.mamba import *

with description('_model._Model constructor'):
  with before.each:
    self.factory = _dimension_factory._DimensionFactory()

  with it('handles simple input'):
    expect(calling(_model._Model, self.factory)).not_to(raise_error)

with description('_model._Model usage'):
  with before.each:
    self.factory = _dimension_factory._DimensionFactory()
    self.model = _model._Model(self.factory)
    self.andy, self.bob = self.factory(name=['andy', 'bob'])
    self.cherries, self.dates = self.factory(fruit=['cherries', 'dates'])
    self._10, self._11 = self.factory(age=[10, 11])

  with description('constraints'):
    with it('accumulates constraints one at a time'):
      expect(self.model.constraints).to(have_len(0))
      self.model(self.andy == self.cherries)
      expect(self.model.constraints).to(have_len(1))
      self.model(self.dates == self.bob)
      expect(self.model.constraints).to(have_len(2))
      self.model(self.cherries != self.bob)
      expect(self.model.constraints).to(have_len(3))

    with it('accumulates constraints all at once'):
      self.model(
          self.andy == self.cherries,
          self.dates == self.bob,
          self.cherries != self.bob,
      )
      expect(self.model.constraints).to(have_len(3))
      expect(str(self.model)).to(look_like("""
        assign:
          name["andy"].fruit["cherries"] in {0,1}
          name["bob"].fruit["dates"] in {0,1}
          name["bob"].fruit["cherries"] in {0,1}

        subject to:
          (name["andy"].fruit["cherries"] == True)
          (name["bob"].fruit["dates"] == True)
          (name["bob"].fruit["cherries"] == False)
      """))

  with description('resolve'):
    with it('resolves simple addresses'):
      reference = self.model.resolve('name["andy"]')
      expect(reference._constraints).to(equal({'name': 'andy'}))

    with it('resolves complex addresses'):
      reference = self.model.resolve('name["andy"].fruit["cherries"]')
      expect(reference._constraints).to(equal({
        'name': 'andy',
        'fruit': 'cherries'
      }))

    with it('resolves values'):
      reference = self.model.resolve_value('cherries')
      expect(reference._constraints).to(equal({
        'fruit': 'cherries',
      }))

    with it('resolves primitives'):
      reference = self.model.resolve_value(11)
      expect(reference).to(be_a(_reference.ValueReference))
      expect(reference.value()).to(equal(11))

  with description('get_variables'):
    with it('returns empty result for empty query'):
      expect(str(self.model.get_variables({}))).to(equal(''))

    with it('returns empty results for weakly constrained query'):
      expect(str(self.model.get_variables({'name': 'andy'}))).to(equal(''))

    with it('returns 1 result for well constrained query'):
      result = self.model.get_variables({
        'name': 'andy',
        'fruit': 'cherries',
      })
      expect(result).to(have_len(1))
      expect(str(result)).to(equal('name["andy"].fruit["cherries"] in {0,1}'))

    with it('returns multiple results for well constrained query'):
      result = self.model.get_variables({
        'name': 'andy',
        'fruit': 'cherries',
        'age': 10,
      })
      expect(result).to(have_len(3))
      expect(str(result)).to(look_like("""
        name["andy"].fruit["cherries"] in {0,1}
        name["andy"].age[10] in {0,1}
        fruit["cherries"].age[10] in {0,1}
      """))

    with it('returns from a cache'):
      result_1 = self.model.get_variables({
        'name': 'andy',
        'fruit': 'cherries',
      })
      result_2 = self.model.get_variables({
        'name': 'andy',
        'fruit': 'cherries',
      })
      expect(result_1).to(have_len(len(result_2)))
      for a, b in zip(result_1, result_2):
        expect(a).to(be(b))

    with it('reifies partially constrained dimensions'):
      result = self.model.get_variables({
        'name': 'bob',
        'age': None,
      })
      expect(str(result)).to(equal(
          '(10*name["bob"].age[10] in {0,1} + 11*name["bob"].age[11] in {0,1})'
      ))

  with description('get_solutions'):
    with it('returns a 3x2 table'):
      self.model(self.andy.cherries[10] == True)
      self.model.load('Mistral').solve()
      column_headings, cells = self.model.get_solutions()
      expect(column_headings).to(have_len(3))
      expect(column_headings).to(equal([
        'name', 'fruit', 'age',
      ]))
      expect(cells).to(have_len(2))
      for row in cells:
        expect(row).to(have_len(3))
      expect(cells).to(equal([
        [['andy'], ['cherries'], [10]],
        [['bob'], ['dates'], [11]],
      ]))

  with description('dimension_constraints'):
    with it('enforces cardinality constraints'):
      result = self.model._dimensional_cardinality_constraints()
      expect(result).to(have_len(12))
      s = '\n'.join(sorted(
          str(result).replace(' | 0 in [1,1] 1 in [1,1] ', '').split('\n')
      ))
      expect(s).to(look_like("""
        (fruit["cherries"].age[10] != fruit["cherries"].age[11])
        (fruit["cherries"].age[10] != fruit["dates"].age[10])
        (fruit["cherries"].age[11] != fruit["dates"].age[11])
        (fruit["dates"].age[10] != fruit["dates"].age[11])
        (name["andy"].age[10] != name["andy"].age[11])
        (name["andy"].age[10] != name["bob"].age[10])
        (name["andy"].age[11] != name["bob"].age[11])
        (name["andy"].fruit["cherries"] != name["andy"].fruit["dates"])
        (name["andy"].fruit["cherries"] != name["bob"].fruit["cherries"])
        (name["andy"].fruit["dates"] != name["bob"].fruit["dates"])
        (name["bob"].age[10] != name["bob"].age[11])
        (name["bob"].fruit["cherries"] != name["bob"].fruit["dates"])
      """))

    with it('enforces inference constraints'):
      result = self.model._dimensional_inference_constraints()
      expect(result).to(have_len(8))
      s = '\n'.join(sorted(
          re.sub(r'\.|name|fruit|age', '', str(result)).split('\n')
      ))
      expect(s).to(look_like("""
        ((["andy"]["cherries"] + ["andy"][10] + ["cherries"][10]) != 2)
        ((["andy"]["cherries"] + ["andy"][11] + ["cherries"][11]) != 2)
        ((["andy"]["dates"] + ["andy"][10] + ["dates"][10]) != 2)
        ((["andy"]["dates"] + ["andy"][11] + ["dates"][11]) != 2)
        ((["bob"]["cherries"] + ["bob"][10] + ["cherries"][10]) != 2)
        ((["bob"]["cherries"] + ["bob"][11] + ["cherries"][11]) != 2)
        ((["bob"]["dates"] + ["bob"][10] + ["dates"][10]) != 2)
        ((["bob"]["dates"] + ["bob"][11] + ["dates"][11]) != 2)
      """))

  with description('load'):
    with it('applies dimensional constraints before loading'):
      expect(str(self.model)).to(look_like("""
        assign:
                 
        subject to:
      """))
      expect(len(self.model.constraints)).to(be(0))
      self.model.load('Mistral')
      expect(len(self.model.constraints)).to(be_above(20))

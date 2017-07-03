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

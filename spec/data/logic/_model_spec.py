from data.logic import _dimension_factory, _model
from spec.mamba import *

with description('_model._Model'):
  with before.each:
    self.factory = _dimension_factory._DimensionFactory()

  with description('constructor'):
    with it('handles simple input'):
      expect(calling(_model._Model, self.factory)).not_to(raise_error)

  with description('constraints'):
    with before.each:
      self.model = _model._Model(self.factory)
      self.andy, self.bob = self.factory(name=['andy', 'bob'])
      self.cherries, self.dates = self.factory(fruit=['cherries', 'dates'])

    with it('accumulates constraints'):
      self.model(
          self.andy == self.cherries,
          self.dates == self.bob,
          self.cherries != self.bob,
      )
      expect(self.model.constraints()).to(have_len(3))

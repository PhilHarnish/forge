import ast

from data.logic import _dimension_factory, _expr_transformer, _model
from spec.mamba import *

with description('_expr_transformer.ExprTransformer'):
  with it('instantiates'):
    expect(calling(_expr_transformer.ExprTransformer, None)).not_to(raise_error)

  with description('compile'):
    with before.each:
      self.factory = _dimension_factory._DimensionFactory()
      self.model = _model._Model(self.factory)
      self.transformer = _expr_transformer.ExprTransformer(self.model)
      self.andy, self.bob = self.name = self.factory(name=['andy', 'bob'])
      self.cherries, self.dates = self.fruit = self.factory(
          fruit=['cherries', 'dates'])

    with it('fails to visit unsupported nodes'):
      expect(calling(self.transformer.compile, ast.Await)).to(
          raise_error(TypeError))
      expect(calling(self.transformer.visit, ast.Await)).to(
          raise_error(NotImplementedError))
      expect(calling(self.transformer.generic_visit, ast.Await)).to(
          raise_error(NotImplementedError))

    with it('supports precise (2d) assignment'):
      expr = self.name['andy'].fruit == self.fruit['cherries']
      expect(self.transformer.compile(expr)).to(be_a(_model._Predicates))

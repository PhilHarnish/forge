import ast

from data.logic import _ast_factory, _dimension_factory
from spec.mamba import *

with description('_ast_factory'):
  with before.each:
    self.factory = _dimension_factory._DimensionFactory()
    self.andy, self.bob = self.factory(name=['andy', 'bob'])
    self.cherries, self.dates = self.factory(fruit=['cherries', 'dates'])

  with description('coerce_operator'):
    with it('supports =='):
      expect(calling(_ast_factory.coerce_operator, '==')).not_to(raise_error)
      expect(_ast_factory.coerce_operator('==')).to(be_a(ast.Eq))

  with description('coerce_value'):
    with it('rejects garbage input'):
      class UnsupportedClass(object):
        pass


      unsupported = UnsupportedClass()
      expect(calling(_ast_factory.coerce_value, unsupported)).to(raise_error)

    with it('supports bool literals'):
      expect(calling(_ast_factory.coerce_value, True)).not_to(raise_error)
      expect(_ast_factory.coerce_value(True)).to(be_a(ast.NameConstant))

    with it('supports number literals'):
      expect(calling(_ast_factory.coerce_value, 1)).not_to(raise_error)
      expect(_ast_factory.coerce_value(1)).to(be_a(ast.Num))
      expect(calling(_ast_factory.coerce_value, 1.5)).not_to(raise_error)
      expect(_ast_factory.coerce_value(1.5)).to(be_a(ast.Num))

    with it('supports str literals'):
      expect(calling(_ast_factory.coerce_value, 'a')).not_to(raise_error)
      expect(_ast_factory.coerce_value('a')).to(be_a(ast.Str))

    with it('supports expressions'):
      node = ast.Expr(value=ast.Load())
      expect(calling(_ast_factory.coerce_value, node)).not_to(raise_error)
      expect(_ast_factory.coerce_value(node)).to(be_a(ast.Load))

    with it('supports all other AST nodes'):
      node = ast.Load()
      expect(calling(_ast_factory.coerce_value, node)).not_to(raise_error)
      expect(_ast_factory.coerce_value(node)).to(be_a(ast.Load))

  with description('binary operations'):
    with it('supports +'):
      expect(_ast_factory.bin_op(self.andy, '+', 1)).to(be_a(ast.Expr))

    with it('supports -'):
      expect(_ast_factory.bin_op(self.andy, '-', 1)).to(be_a(ast.Expr))

    with it('supports |'):
      expect(_ast_factory.bin_op(self.andy, '|', True)).to(be_a(ast.Expr))

    with it('supports ^'):
      expect(_ast_factory.bin_op(self.andy, '|', False)).to(be_a(ast.Expr))

    with it('supports *'):
      expect(_ast_factory.bin_op(self.andy, '*', 12)).to(be_a(ast.Expr))

    with it('supports &'):
      expect(_ast_factory.bin_op(self.bob, '&', self.dates)).to(be_a(ast.Expr))

  with description('compare'):
    with it('rejects invalid input'):
      expect(calling(_ast_factory.compare, None, [], [])).to(raise_error)

    with it('accepts simple input'):
      expect(
          calling(_ast_factory.compare, self.andy, ['=='], [self.cherries])
      ).not_to(raise_error)
      expect(_ast_factory.compare(self.andy, ['=='], [self.cherries])).to(be_a(
          ast.Expr))

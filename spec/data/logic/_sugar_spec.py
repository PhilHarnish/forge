import ast

from data.logic import _ast_factory, _sugar
from spec.mamba import *

with description('_sugar.sugar_abs'):
  with it('accepts ordinary numbers'):
    expect(_sugar.sugar_abs(-1)).to(equal(1))

  with it('accumulates expressions if passed an accumulating expression'):
    expr = ast.Expr()
    expect(_sugar.sugar_abs(expr)).to(
        be_a(_ast_factory.AccumulatingExpressionMixin))

with description('_sugar.sugar_all'):
  with it('accepts empty list'):
    expect(_sugar.sugar_all([])).to(
        be_a(_ast_factory.AccumulatingExpressionMixin))

  with it('produces a valid Numberjack.Conjunction call'):
    sugar_all = _sugar.sugar_all([1, 2, 3])
    expect(sugar_all.func.id).to(equal('Conjunction'))
    expect(sugar_all.args).to(have_len(1))
    expect(sugar_all.args[0]).to(be_a(ast.List))

with description('_sugar.sugar_any'):
  with it('accepts empty list'):
    expect(_sugar.sugar_any([])).to(
        be_a(_ast_factory.AccumulatingExpressionMixin))

  with it('produces a valid Numberjack.Disjunction call'):
    sugar_any = _sugar.sugar_any([1, 2, 3])
    expect(sugar_any.func.id).to(equal('Disjunction'))
    expect(sugar_any.args).to(have_len(1))
    expect(sugar_any.args[0]).to(be_a(ast.List))

with description('_sugar.sugar_sum'):
  with it('accepts empty list'):
    expect(_sugar.sugar_sum([])).to(
        be_a(_ast_factory.AccumulatingExpressionMixin))

  with it('produces a valid Numberjack.Disjunction call'):
    sugar_sum = _sugar.sugar_sum([1, 2, 3])
    expect(sugar_sum.func.id).to(equal('Sum'))
    expect(sugar_sum.args).to(have_len(1))
    expect(sugar_sum.args[0]).to(be_a(ast.List))

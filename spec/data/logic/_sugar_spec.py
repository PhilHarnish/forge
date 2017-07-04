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

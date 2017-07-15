import ast

from data.logic import _ast_factory, _sugar
from spec.mamba import *

with description('_sugar.wrapped_call'):
  with before.each:
    self.subject = _sugar.wrapped_call(sum)

  with it('accepts empty list'):
    expect(self.subject([])).to(
        be_a(_ast_factory.AccumulatingExpressionMixin))

  with it('produces a valid Numberjack.Conjunction call'):
    sugar_all = self.subject([1, 2, 3])
    expect(sugar_all.func).to(equal(sum))
    expect(sugar_all.args).to(have_len(1))
    expect(sugar_all.args[0]).to(be_a(ast.List))

with description('_sugar.deferred_call'):
  with before.each:
    self.fn = mock.Mock()
    self.subject = _sugar.deferred_call(self.fn)

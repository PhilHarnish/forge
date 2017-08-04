import ast

from data.logic import _dimension_factory, _expr_transformer, _model, \
  _predicates, _reference, dsl
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
    self._10, self._11 = self.age = self.factory(age=[10, 11])

  with it('resolves names'):
    node = ast.Name(id='name["andy"].fruit["cherries"]', ctx=ast.Load())
    transformed = self.transformer.visit(node)
    expect(transformed).to(be_a(_reference.Reference))
    expect(transformed._constraints).to(equal({
      'name': 'andy',
      'fruit': 'cherries'
    }))

  with it('resolves numbers'):
    node = ast.Num(n=10)
    transformed = self.transformer.visit(node)
    expect(transformed).to(be_a(_reference.Reference))
    expect(transformed._constraints).to(equal({'age': 10}))

  with it('resolves strings'):
    node = ast.Str(s='cherries')
    transformed = self.transformer.visit(node)
    expect(transformed).to(be_a(_reference.Reference))
    expect(transformed._constraints).to(equal({'fruit': 'cherries'}))

  with it('fails to visit unsupported nodes'):
    expect(calling(self.transformer.compile, ast.Await)).to(
        raise_error(NotImplementedError))
    expect(calling(self.transformer.visit, ast.Await)).to(
        raise_error(NotImplementedError))
    expect(calling(self.transformer.generic_visit, ast.Await)).to(
        raise_error(NotImplementedError))

  with it('supports precise (2d) assignment'):
    expr = self.name['andy'].fruit == self.fruit['cherries']
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal(
        '(name["andy"].fruit["cherries"] == True)'))

  with it('supports OR operation'):
    expr = (self.name['andy'].fruit['cherries'] |
            self.fruit['cherries'].name['bob'])
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal(
        '(name["andy"].fruit["cherries"] or name["bob"].fruit["cherries"])'))

  with it('supports XOR operation'):
    expr = (self.name['andy'].fruit['cherries'] ^
            self.fruit['cherries'].name['bob'])
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal(
        '((name["andy"].fruit["cherries"] +'
        ' name["bob"].fruit["cherries"]) == 1)'))

  with it('supports + operation, int on right'):
    expr = self.name['andy'].age + 2
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal('(name["andy"].age in {10,11} + 2)'))

  with it('supports + operation, int on left'):
    expr = 2 + self.name['andy'].age
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal('(2 + name["andy"].age in {10,11})'))

  with it('supports - operation, int on right'):
    expr = self.name['andy'].age - 2
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal('(name["andy"].age in {10,11} - 2)'))

  with it('supports - operation, int on left'):
    expr = 2 - self.name['andy'].age
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal('(2 - name["andy"].age in {10,11})'))

  with it('supports * operation, int on right'):
    expr = self.name['andy'].age[10] * 10
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal('((name["andy"].age == 10) * 10)'))

  with it('supports * operation, int on left'):
    expr = 10 * self.name['andy'].age[10]
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    # For some reason(?) the operations are switched here.
    expect(str(compiled)).to(equal('((name["andy"].age == 10) * 10)'))

  with it('supports & operation'):
    expr = self.andy[10] & self.bob[11]
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal(
        '((name["andy"].age == 10) & (name["bob"].age == 11))'))

  with it('supports ~ operation'):
    expr = ~self.andy[10]
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal(
        '((1 - (name["andy"].age == 10)) == True)'))

  with it('supports call expressions'):
    expr = dsl.abs(self.andy.age - self.bob.age)
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    # For some reason(?) the operations are switched here.
    s = str(compiled).replace(' in {0,1}', '')
    expect(s).to(equal(
        'Abs((name["andy"].age in {10,11} -'
        ' name["bob"].age in {10,11}))'
    ))

  with it('supports naked _DimensionSlice expressions'):
    expr = self.name['andy'].age[10]
    compiled = self.transformer.compile(expr)
    expect(compiled).to(be_a(_predicates.Predicates))
    expect(str(compiled)).to(equal('((name["andy"].age == 10) == True)'))

  with it('supports Call with builtin functions'):
    expr = ast.parse('max(1, 3)').body[0]
    compiled = self.transformer.compile(expr)
    expect(str(compiled)).to(equal('3'))

  with it('supports Call with function pointers'):
    fn = mock.Mock(return_value=3)
    expr = ast.Call(
        func=fn,
        args=[],
        keywords=[],
    )
    compiled = self.transformer.compile(expr)
    expect(fn).to(have_been_called)
    expect(str(compiled)).to(equal('3'))

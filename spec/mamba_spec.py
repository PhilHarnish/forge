from spec.mamba import *

with description('mamba test helper'):
  with description('call'):
    with it('reprs empty fns'):
      def example():
        pass
      expect(repr(call(example))).to(equal('example()'))

    with it('reprs functions with simple args'):
      def example(a, b):
        pass
      expect(repr(call(example, 1, 2))).to(equal('example(1, 2)'))

    with it('reprs functions with kwargs'):
      def example(a, b=None):
        pass
      expect(repr(call(example, 1, b=2))).to(equal('example(1, b=2)'))

  with context('operator overloading'):
    with before.each:
      self.bool_fn = lambda *args, **kwargs: True
      self.int_fn = lambda *args, **kwargs: 1
      self.str_fn = lambda *args, **kwargs: 'ex'

    with it('supports bool checks'):
      expect(call(self.bool_fn)).to(equal(True))

    with it('supports inequality checks'):
      expect(call(self.int_fn)).to(be_above(0.5))
      expect(call(self.int_fn)).to(be_above_or_equal(1))
      expect(call(self.int_fn)).to(be_below_or_equal(1))
      expect(call(self.int_fn)).to(be_below(1.5))

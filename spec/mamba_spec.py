from spec.mamba import *

with description('mamba test helper'):
  with description('call'):
    with it('reprs empty fns'):
      def example():
        pass
      expect(repr(call(example))).to(equal('example()'))

    with it('reprs functions with simple args'):
      def example(a, b):
        return a + b
      expect(repr(call(example, 1, 2))).to(equal('example(1, 2) == 3'))

    with it('reprs functions with kwargs'):
      def example(a, b=None):
        return a + b
      expect(repr(call(example, 1, b=2))).to(equal('example(1, b=2) == 3'))

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

  with description('calling'):
    with before.all:
      def bomb():
        raise NotImplementedError()
      self.bomb = bomb

    with it('should not execute function when instantiated'):
      expect(self.bomb).to(raise_error)
      expect(lambda: calling(self.bomb)).not_to(raise_error)

    with it('should execute function when matcher runs'):
      expect(calling(self.bomb)).to(raise_error)

  with description('be_between'):
    with it('should accept numbers between high and low'):
      expect(1).to(be_between(0, 2))

    with it('should reject numbers matching high or low'):
      expect(0).not_to(be_between(0, 1))
      expect(1).not_to(be_between(0, 1))

  with description('be_one_of'):
    with it('should accept a single option'):
      expect(1).to(be_one_of(1))

    with it('should mismatches'):
      expect(0).not_to(be_one_of(1))

    with it('should accept from a list'):
      expect(0).to(be_one_of(*range(3)))
      expect(1).to(be_one_of(*range(3)))
      expect(2).to(be_one_of(*range(3)))

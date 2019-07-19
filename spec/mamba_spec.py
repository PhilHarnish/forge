import io
import sys

from spec.mamba import *

with description('mamba test helper'):
  with description('call'):
    with it('reprs empty fns'):
      def example() -> None:
        pass
      expect(repr(call(example))).to(equal('example()'))

    with it('reprs functions with simple args'):
      def example(a: int, b: int) -> int:
        return a + b
      expect(repr(call(example, 1, 2))).to(equal('example(1, 2) == 3'))

    with it('reprs functions with kwargs'):
      def example(a: int, b: int=None) -> int:
        return a + b
      expect(repr(call(example, 1, b=2))).to(equal('example(1, b=2) == 3'))

    with it('pretends to be instanceof value'):
      def example(x: Any) -> Any:
        return x
      expect(call(example, 1)).to(be_an(int))
      expect(call(example, 'test')).to(be_a(str))

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
      def bomb() -> None:
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

  with description('be_unique'):
    with it('should accept empty input'):
      expect([]).to(be_unique)

    with it('should accept unique str iterable'):
      expect('asdf').to(be_unique)

    with it('should accept unique list iterable'):
      expect([1, 2, 3]).to(be_unique)

    with it('should reject list with duplicates'):
      expect([1, 2, 3, 3]).not_to(be_unique)

    with it('should reject iterable with duplicates'):
      expect(sorted([1, 2, 3, 3])).not_to(be_unique)

  with description('look like'):
    with it('should normally behave like equals'):
      expect('a').to(look_like('a'))
      expect('asdf').to(look_like('asdf'))
      expect('a s d f').to(look_like('a s d f'))

    with it('should accept inputs with newlines'):
      expect('l\n' * 5).to(look_like('l\n' * 5))

    with it('should accept inputs with crazy indentation'):
      expected = """
                  this
                    is
                      an
                        example
      """
      actual = """
      this
        is
          an
            example"""
      expect(expected).to(look_like(actual))

    with it('removes comments'):
      expected = """
        one
        two "#comment"
        three
      """
      actual = """
        one  # Line with a comment.
        two "#comment"
        # Comment above a line.
        three
      """
      expect(expected).to(look_like(actual, remove_comments=True))

  with description('mocks'):
    with before.each:
      self.subject = mock.Mock(name='mamba_mock')

    with it('should observe non-calls'):
      expect(self.subject).not_to(have_been_called)

    with it('should allow specifying args for non-calls'):
      expect(self.subject).not_to(have_been_called_with('asdf'))

    with it('should detect calls'):
      self.subject(1, key='value')
      expect(self.subject).to(have_been_called)

    with it('should detect calls with args'):
      self.subject(1, key='value')
      expect(self.subject).to(have_been_called_with(1, key='value'))

    with it('should handle negation'):
      self.subject(1, key='value')
      expect(self.subject).not_to(have_been_called_with(2, key='other'))

    with it('should call counts'):
      expect(self.subject).to(have_been_called_times(0))
      self.subject()
      expect(self.subject).to(have_been_called_times(1))
      self.subject()
      expect(self.subject).to(have_been_called_times(2))

    with it('should support called once shorthand'):
      expect(self.subject).not_to(have_been_called_once)
      self.subject()
      expect(self.subject).to(have_been_called_once)
      self.subject()
      expect(self.subject).not_to(have_been_called_once)

with description('benchmarks'):
  with it('should work without call()'):
    def test() -> None:
      with benchmark:
        expect(True).to(be_true)
    expect(test).not_to(raise_error)

  with it('should be customizable by calling with arguments'):
    def test() -> None:
      with benchmark(1, 1):
        expect(True).to(be_true)
    expect(test).not_to(raise_error)

  with it('should permit exceptions to raise to the top'):
    class CustomException(Exception):
      pass

    def test() -> None:
      with benchmark(1, 1):
        raise CustomException('exception')
    expect(test).to(raise_error(CustomException))


with description('path_values'):
  with it('echos input for empty input'):
    expect(path_values({}, '')).to(look_like('{}'))

  with it('works for shallow dicts'):
    expect(path_values({'key': 'value'}, ['key'])).to(look_like("""
        {'key': 'value'}
        key = 'value'
    """))

  with it('works for deeper dicts'):
    expect(path_values({'a': {'b': 'c'}}, 'ab')).to(look_like("""
        {'a': {'b': 'c'}}
        a = {'b': 'c'}
        b = 'c'
    """))

  with it('works for arrays and strings'):
    expect(path_values(
        [[['00'], ['01']], [['10'], ['11']]],
        [0, 1, 0, 1])
    ).to(look_like("""
        [[['00'], ['01']], [['10'], ['11']]]
        0 = [['00'], ['01']]
        1 = ['01']
        0 = '01'
        1 = '1'
    """))


with description('traceback') as self:
  with before.each:
    self._stdout = sys.stdout
    self._io = io.StringIO()
    sys.stdout = self._io

  with after.each:
    sys.stdout = self._stdout

  with it('should print output'):
    traceback()
    last_line = self._io.getvalue().splitlines()[-1].strip()
    expect(last_line).to(equal('traceback()'))

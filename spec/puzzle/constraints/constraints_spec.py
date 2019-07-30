from puzzle.constraints import constraints, validator
from spec.mamba import *


class TestConstraints(constraints.Constraints):
  str_with_default: str = 'default'
  optional_str_with_default: Optional[str] = 'optional default'
  optional_with_collection: Optional[List[int]] = [1, 2]
  optional_tuple: Optional[Tuple[int, str, float]] = (1, 'two', 3.0)

class InheritedConstraints(TestConstraints):
  int_with_default: int = 42


class ValidatedConstraints(constraints.Constraints):
  int_in_range: validator.NumberInRange(0, 100) = 42
  optional_int_in_range: Optional[validator.NumberInRange(0, 1)] = None
  float_in_range: validator.NumberInRange(0, 1) = 0.5


with description('constraints'):
  with description('constructor'):
    with it('constructs without error'):
      expect(calling(constraints.Constraints)).not_to(raise_error)

  with description('value validation') as self:
    with before.each:
      self.ex = TestConstraints()

    with it('provides default values'):
      expect(self.ex.str_with_default).to(equal('default'))

    with it('allows modifications within a type'):
      expect(calling(setattr, self.ex, 'str_with_default', 'foobar')).not_to(
          raise_error)
      expect(self.ex.str_with_default).to(equal('foobar'))

    with it('forbids modifications outside of a type'):
      expect(calling(setattr, self.ex, 'str_with_default', False)).to(
          raise_error(ValueError))
      expect(self.ex.str_with_default).to(equal('default'))

    with it('allows modification to optional types'):
      expect(calling(setattr, self.ex, 'optional_str_with_default',
          'foobar')).not_to(raise_error)
      expect(self.ex.optional_str_with_default).to(equal('foobar'))

    with it('allows None for optional types'):
      expect(calling(setattr, self.ex, 'optional_str_with_default',
          None)).not_to(raise_error)
      expect(self.ex.optional_str_with_default).to(equal(None))

    with it('allows reassigning None to optional collection'):
      expect(calling(setattr, self.ex, 'optional_with_collection',
          None)).not_to(raise_error)
      expect(self.ex.optional_with_collection).to(equal(None))

    with it('allows reassigning collection to collection'):
      expect(calling(setattr, self.ex, 'optional_with_collection',
          [3, 4])).not_to(raise_error)
      expect(self.ex.optional_with_collection).to(equal([3, 4]))

    with it('rejects assigning invalid type'):
      expect(calling(setattr, self.ex, 'optional_with_collection',
          4)).to(raise_error)
      expect(self.ex.optional_with_collection).to(equal([1, 2]))

    with it('rejects assigning incorrect collection type'):
      expect(calling(setattr, self.ex, 'optional_with_collection',
          (3, 4))).to(raise_error)
      expect(self.ex.optional_with_collection).to(equal([1, 2]))

    with it('allows reassigning None to optional tuple'):
      expect(calling(setattr, self.ex, 'optional_tuple',
          None)).not_to(raise_error)
      expect(self.ex.optional_tuple).to(equal(None))

    with it('allows reassigning collection to collection'):
      expect(calling(setattr, self.ex, 'optional_tuple',
          (4, 'five', 6.0))).not_to(raise_error)
      expect(self.ex.optional_tuple).to(equal((4, 'five', 6.0)))

    with it('rejects assigning invalid type'):
      expect(calling(setattr, self.ex, 'optional_tuple', 4)).to(raise_error)
      expect(self.ex.optional_tuple).to(equal((1, 'two', 3.0)))

    with it('rejects assigning incorrect collection type'):
      expect(calling(setattr, self.ex, 'optional_tuple',
          [3, 4])).to(raise_error)
      expect(self.ex.optional_tuple).to(equal((1, 'two', 3.0)))

    with description('inheritance') as self:
      with before.each:
        self.ex = InheritedConstraints()

      with it('provides new default values'):
        expect(self.ex.int_with_default).to(equal(42))

      with it('provides original default values'):
        expect(self.ex.str_with_default).to(equal('default'))

      with it('allows modifications to new values'):
        expect(calling(setattr, self.ex, 'int_with_default', 12)).not_to(
            raise_error)
        expect(self.ex.int_with_default).to(equal(12))

      with it('allows modifications to original values'):
        expect(calling(setattr, self.ex, 'optional_str_with_default',
            None)).not_to(raise_error)
        expect(self.ex.optional_str_with_default).to(equal(None))

  with description('validated constraints') as self:
    with before.each:
      self.ex = ValidatedConstraints()

    with it('provides defaults'):
      expect(self.ex.int_in_range).to(equal(42))

    with it('accepts valid mutations'):
      expect(calling(setattr, self.ex, 'int_in_range', 12)).not_to(raise_error)
      expect(self.ex.int_in_range).to(equal(12))

    with it('rejects invalid mutations'):
      expect(calling(setattr, self.ex, 'int_in_range', 200)).to(raise_error)
      expect(self.ex.int_in_range).to(equal(42))

    with it('allows clearing optional values'):
      expect(calling(setattr, self.ex, 'optional_int_in_range',
          None)).not_to(raise_error)
      expect(self.ex.optional_int_in_range).to(equal(None))

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


class T(object):
  def __eq__(self, other: Any) -> bool:
    return NotImplemented


with description('constraints.Constraints'):
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

    with description('inheritance'):
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

  with description('observing changes'):
    with it('notifies subscribers of changes'):
      ex = TestConstraints()
      subscriber = mock.Mock()
      ex.subscribe(subscriber)
      ex.str_with_default = 'foobar'
      expect(subscriber.on_next).to(have_been_called_once)
      expect(subscriber.on_next).to(have_been_called_with(
          (ex, 'str_with_default', 'default', 'foobar')))

    with it('no-op changes are not broadcast'):
      ex = TestConstraints()
      subscriber = mock.Mock()
      ex.subscribe(subscriber)
      ex.str_with_default = 'default'
      expect(subscriber.on_next).not_to(have_been_called)

    with it('missed changes are not queued'):
      ex = TestConstraints()
      subscriber = mock.Mock()
      ex.str_with_default = 'foobar'
      ex.subscribe(subscriber)
      expect(subscriber.on_next).not_to(have_been_called)

  with description('__iter__'):
    with it('yields information needed to reflectively constrain'):
      expect(list(TestConstraints())).to(have_len(4))

    with it('includes inherited constraints'):
      expect(list(InheritedConstraints())).to(have_len(5))

    with it('includes type information'):
      types = {k: t for k, _, t in TestConstraints()}
      expect(types).to(have_key('str_with_default', str))
      expect(types).to(
          have_key('optional_with_collection', Optional[List[int]]))

  with description('__str__'):
    with it('produces readable output for base class'):
      expect(str(TestConstraints())).to(look_like("""
        optional_str_with_default = 'optional default'
        optional_tuple = (1, 'two', 3.0)
        optional_with_collection = [1, 2]
        str_with_default = 'default'
      """))

    with it('produces readable output for descendent class'):
      expect(str(InheritedConstraints())).to(look_like("""
        int_with_default = 42
        optional_str_with_default = 'optional default'
        optional_tuple = (1, 'two', 3.0)
        optional_with_collection = [1, 2]
        str_with_default = 'default'
      """))


with description('unwrap_optional'):
  with it('returns None if Optional is not used'):
    expect(calling(constraints.unwrap_optional, int)).to(equal(None))
    expect(calling(constraints.unwrap_optional, tuple)).to(equal(None))

  with it('returns type when Optional is used'):
    expect(constraints.unwrap_optional(Optional[T])).to(equal(T))

  with it('returns type when Union is used'):
    expect(constraints.unwrap_optional(Union[None, T])).to(equal(T))
    expect(constraints.unwrap_optional(Union[T, None])).to(equal(T))

  with it('returns None if Union is used with multiple types'):
    expect(calling(constraints.unwrap_optional, Union[None, int, float])).to(
        equal(None))

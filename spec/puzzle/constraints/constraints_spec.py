from puzzle.constraints import constraints, validator
from spec.mamba import *


class TestConstraints(constraints.Constraints):
  str_with_default: str = 'default'
  optional_str_with_default: Optional[str] = 'optional default'
  optional_with_collection: Optional[List[int]] = [1, 2]
  optional_tuple: Optional[Tuple[int, str, float]] = (1, 'two', 3.0)


class DocumentedConstraints(constraints.Constraints):
  """Documented constraints.

  a: Sample constraint.
  z: A non-alphabetical constraint.
  b: Another constraint,
     this time with line wrapping.
  c: A final constraint.
  """
  a: str = 'a'
  z: str = 'z'
  b: Optional[int] = None
  c: float = 1.5


class DynamicConstraints(constraints.Constraints):
  dynamic_constraint: validator.NumberInRange(min_value=0) = 0
  _dynamic_annotation: validator.NumberInRange = None
  _last_change: Optional[constraints.ConstraintChangeEvent] = None

  def __init__(self, max_value: int) -> None:
    self._dynamic_annotation = validator.NumberInRange(
        min_value=0, max_value=max_value)
    self._last_change = None
    super().__init__()

  def _resolve_annotation(self, k: str) -> Optional[type]:
    if k == 'dynamic_constraint':
      return self._dynamic_annotation
    return super()._resolve_annotation(k)

  def _before_change_event(
      self, event: constraints.ConstraintChangeEvent) -> None:
    self._last_change = event

  def get_last_change(self) -> Optional[constraints.ConstraintChangeEvent]:
    return self._last_change

  # Exposed for testing.
  pause_events = constraints.Constraints._pause_events



class InheritedConstraints(TestConstraints):
  int_with_default: int = 42


class OrderedConstraints(constraints.Constraints):
  _ordered_keys: List[str] = ['ordered_a', 'ordered_z', 'ordered_b']
  ordered_a: bool = True
  ordered_b: bool = True
  ordered_z: bool = True


class ValidatedConstraints(constraints.Constraints):
  int_in_range: validator.NumberInRange(0, 100) = 42
  optional_int_in_range: Optional[validator.NumberInRange(0, 1)] = None
  float_in_range: validator.NumberInRange(0, 1) = 0.5
  not_modifiable: bool = True

  def is_modifiable(self, key: str) -> bool:
    return key != 'not_modifiable'


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

  with description('dynamic constraints'):
    with it('provides defaults'):
      expect(DynamicConstraints(0).dynamic_constraint).to(equal(0))

    with it('enforces dynamic constraint'):
      ex = DynamicConstraints(10)
      expect(calling(setattr, ex, 'dynamic_constraint', 11)).to(raise_error(
          ValueError,
          'DynamicConstraints.dynamic_constraint must be'
          ' NumberInRange(min_value=0, max_value=10) (11 given)'
      ))

    with it('allows preparatory work before events fire'):
      c = DynamicConstraints(5)
      expect(c.get_last_change()).to(be_none)

      @mock_wrap
      def callback(change: constraints.ConstraintChangeEvent):
        expect(c.get_last_change()).to(equal(change))

      c.subscribe(callback)
      c.dynamic_constraint = 1
      expect(callback).to(have_been_called)

    with it('hides internal state'):
      expect(str(DynamicConstraints(0))).to(look_like("""
        dynamic_constraint = 0
      """))

    with it('allows broadcasts to be paused'):
      c = DynamicConstraints(5)
      subscriber = mock.Mock()
      c.subscribe(subscriber)
      with c.pause_events():
        c.dynamic_constraint = 3
      expect(subscriber.on_next).not_to(have_been_called)
      c.dynamic_constraint = 2
      expect(subscriber.on_next).to(have_been_called)

    with it('queues broadcasts and flushes at the end'):
      c = DynamicConstraints(5)
      subscriber = mock.Mock()
      c.subscribe(subscriber)
      with c.pause_events(flush=True):
        c.dynamic_constraint = 3
        expect(subscriber.on_next).not_to(have_been_called)
      expect(subscriber.on_next).to(have_been_called)

    with it('does not broadcast None'):
      c = DynamicConstraints(5)
      subscriber = mock.Mock()
      c.subscribe(subscriber)
      with c.pause_events(flush=True):
        expect(subscriber.on_next).not_to(have_been_called)
      expect(subscriber.on_next).not_to(have_been_called)

    with it('queues broadcasts and remembers history'):
      c = DynamicConstraints(5)
      subscriber = mock.Mock()
      c.subscribe(subscriber)
      with c.pause_events():
        c.dynamic_constraint = 3
      c.dynamic_constraint = 2
      expect(subscriber.on_next).to(have_been_called_with(
          (c, 'dynamic_constraint', 3, 2, (
            (c, 'dynamic_constraint', 0, 3, None)
          ))
      ))

    with it('allows recursive pausing'):
      c = DynamicConstraints(5)
      subscriber = mock.Mock()
      c.subscribe(subscriber)
      with c.pause_events():
        with c.pause_events():
          with c.pause_events():
            c.dynamic_constraint = 4
          c.dynamic_constraint = 3
        c.dynamic_constraint = 2
      c.dynamic_constraint = 1
      expect(subscriber.on_next).to(have_been_called_times(1))

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
          (ex, 'str_with_default', 'default', 'foobar', None)))

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

  with description('is_modifiable'):
    with it('returns True by default'):
      ex = TestConstraints()
      expect(ex.is_modifiable('str_with_default')).to(be_true)

    with it('returns True by default'):
      ex = ValidatedConstraints()
      expect(ex.is_modifiable('not_modifiable')).to(be_false)

    with it('assignment enforces is_modifiable'):
      ex = ValidatedConstraints()
      expect(calling(setattr, ex, 'not_modifiable', False)).to(
          raise_error(AttributeError, 'not_modifiable is not modifiable'))

  with description('__iter__'):
    with it('yields information needed to reflectively constrain'):
      expect(list(TestConstraints())).to(have_len(4))

    with it('includes inherited constraints'):
      expect(list(InheritedConstraints())).to(have_len(5))

    with it('includes type information'):
      types = {k: t for k, _, t, _ in TestConstraints()}
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

    with it('allows ordering keys'):
      expect(str(OrderedConstraints())).to(look_like("""
        ordered_a = True
        ordered_z = True
        ordered_b = True
      """))

    with it('includes docs'):
      expect(str(DocumentedConstraints())).to(look_like("""
        a = 'a'  # Sample constraint.
        z = 'z'  # A non-alphabetical constraint.
        b = None  # Another constraint, this time with line wrapping.
        c = 1.5  # A final constraint.
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

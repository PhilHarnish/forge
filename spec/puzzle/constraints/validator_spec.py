import enum

from puzzle.constraints import validator
from spec.mamba import *


class TestEnum(enum.Enum):
  DEFAULT = enum.auto()
  DEFINED = enum.auto()


with description('validator'):
  with description('constructor'):
    with it('constructs without error'):
      expect(calling(validator.Validator, object)).not_to(raise_error)

  with description('typing compatibility'):
    with it('is permitted for use with typing module'):
      def type_usage() -> None:
        noop = Union[validator.Validator(object)]
        del noop
      expect(calling(type_usage)).not_to(raise_error)


with description('Enum'):
  with description('constructor'):
    with it('constructs without error'):
      expect(calling(validator.Enum, enum.Enum)).not_to(raise_error)

    with it('raises for incorrect types'):
      expect(calling(validator.Enum, float)).to(raise_error(
          TypeError, 'Validator.Enum requires an enum.Enum (float given)'))

    with it('accepts sample values'):
      v = validator.Enum(TestEnum)
      expect(TestEnum.DEFAULT).to(be_a(v))


with description('NumberInRange'):
  with description('constructor'):
    with it('constructs without error'):
      expect(calling(validator.NumberInRange, 1, 5)).not_to(raise_error)

    with it('rejects missing arguments'):
      expect(calling(validator.NumberInRange)).to(raise_error)

  with description('instance checks'):
    with it('accepts numbers within range (int)'):
      v = validator.NumberInRange(1, 5)
      expect(4).to(be_a(v))

    with it('accepts numbers within range (float'):
      v = validator.NumberInRange(1.0, 5.0)
      expect(4.0).to(be_a(v))

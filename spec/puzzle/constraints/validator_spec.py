from puzzle.constraints import validator
from spec.mamba import *

with description('validator'):
  with description('constructor'):
    with it('constructs without error'):
      expect(calling(validator.Validator)).not_to(raise_error)

  with description('typing compatibility'):
    with it('is permitted for use with typing module'):
      def type_usage() -> None:
        noop = Union[validator.Validator()]
        del noop
      expect(calling(type_usage)).not_to(raise_error)


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

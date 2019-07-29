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

    with it('rejects mismatched types'):
      expect(calling(validator.NumberInRange, 2, 2.0)).to(raise_error)

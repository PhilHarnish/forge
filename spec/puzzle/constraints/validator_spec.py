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


with description('Color'):
  with description('constructor'):
    with it('constructs without error, no args'):
      expect(calling(validator.Color)).not_to(raise_error)

    with it('constructs without error, with args'):
      expect(calling(validator.Color, n_channels=1, flat=True)).not_to(
          raise_error)

    with it('validates `flat` is possible'):
      expect(calling(validator.Color, n_channels=4, flat=True)).to(raise_error)

  with description('coerce') as self:
    with before.each:
      def expect_cases_match(
          color: validator.Color, cases: List[Tuple[str, Union[int, type]]]
      ) -> None:
        for given, expected in cases:
          if expected is ValueError:
            expect(calling(color.coerce, given)).to(raise_error(expected))
          else:
            expect(calling(color.coerce, given)).to(equal(expected))


      self.expect_cases_match = expect_cases_match

    with it('coerces 1 channel (flat)'):
      self.expect_cases_match(validator.Color(n_channels=1, flat=True), [
        ('0', 0),
        ('14', 0x14),
        ('#ff', 0xff),
        ('#fff', 0xff),
        ('#ffff', 0xff),
        ('#ffffff', 0xff),
        ('garbage', ValueError),
        ('#ff9966', ValueError),
        ('#ff996600', ValueError),
      ])

    with it('coerces 1 channel (not flat)'):
      self.expect_cases_match(validator.Color(n_channels=1, flat=False), [
        ('0', [0]),
        ('14', [0x14]),
        ('#ff', [0xff]),
        ('#fff', [0xff]),
        ('#ffff', [0xff]),
        ('#ffffff', [0xff]),
        ('garbage', ValueError),
        ('#ff9966', ValueError),
        ('#ff996600', ValueError),
      ])

    with it('coerces 3 channels'):
      self.expect_cases_match(validator.Color(n_channels=3, flat=False), [
        ('0', [0, 0, 0]),
        ('14', [0x14, 0x14, 0x14]),
        ('#ff', [0xff, 0xff, 0xff]),
        ('#fff', [0xff, 0xff, 0xff]),
        ('#ffff', ValueError),
        ('#ffffff', [0xff, 0xff, 0xff]),
        ('garbage', ValueError),
        ('#ff9966', [0xff, 0x99, 0x66]),
        ('#ff996600', ValueError),
      ])

  with description('to_rgb_hex'):
    with it('accepts an int'):
      v = validator.Color(n_channels=1, flat=True)
      expect(v.to_rgb_hex(255)).to(equal('#ffffff'))

    with it('accepts 3 ints (tuple)'):
      v = validator.Color(n_channels=3, flat=False)
      expect(calling(v.to_rgb_hex, (255, 128, 0))).to(equal('#ff8000'))

    with it('accepts 3 ints (list)'):
      v = validator.Color(n_channels=3, flat=False)
      expect(calling(v.to_rgb_hex, [255, 128, 0])).to(equal('#ff8000'))

    with it('rejects short input'):
      v = validator.Color(n_channels=4, flat=False)
      expect(calling(v.to_rgb_hex, (255, 128, 0))).to(raise_error(ValueError))

    with it('rejects long input'):
      v = validator.Color(n_channels=1, flat=False)
      expect(calling(v.to_rgb_hex, (255, 128, 0))).to(raise_error(ValueError))


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

    with it('accepts numbers within range (float)'):
      v = validator.NumberInRange(1.0, 5.0)
      expect(4.0).to(be_a(v))


with description('Point'):
  with description('constructor'):
    with it('constructs without error'):
      expect(calling(validator.Point, 1, 5)).not_to(raise_error)

    with it('rejects missing arguments'):
      expect(calling(validator.Point)).to(raise_error)

  with description('instance checks'):
    with it('accepts numbers within range (int)'):
      v = validator.Point(5, 5)
      expect((2, 3)).to(be_a(v))

    with it('accepts numbers within range (float)'):
      v = validator.Point(5.0, 5.0)
      expect((2.0, 4.0)).to(be_a(v))

    with it('rejects numbers outside range'):
      v = validator.Point(1, 5)
      expect((2, 30)).not_to(be_a(v))

  with description('from_str'):
    with it('produces lists of ints'):
      v = validator.Point(5, 5)
      expect(v.from_str('0, 4')).to(equal((0, 4)))

    with it('produces lists of floats'):
      v = validator.Point(5.0, 5.0)
      expect(v.from_str('[0.5, 4.5]')).to(equal((0.5, 4.5)))

    with it('strips noise'):
      v = validator.Point(5, 5)
      expect(v.from_str('   ([(0, 4)])   ')).to(equal((0, 4)))

with description('RangeInRange'):
  with description('constructor'):
    with it('constructs without error'):
      expect(calling(validator.RangeInRange, 1, 5)).not_to(raise_error)

    with it('rejects missing arguments'):
      expect(calling(validator.RangeInRange)).to(raise_error)

  with description('instance checks'):
    with it('accepts numbers within range (int)'):
      v = validator.RangeInRange(1, 5)
      expect((2, 3)).to(be_a(v))

    with it('accepts numbers within range (float)'):
      v = validator.RangeInRange(1.0, 5.0)
      expect((2.0, 4.0)).to(be_a(v))

    with it('rejects numbers outside range'):
      v = validator.RangeInRange(1, 5)
      expect((2, 30)).not_to(be_a(v))

    with it('rejects numbers in wrong order'):
      v = validator.RangeInRange(1, 5)
      expect((3, 2)).not_to(be_a(v))

from data.graph import bloom_mask
from spec.mamba import *


with description('bits'):
  with it('returns nothing for 0'):
    expect(list(bloom_mask.bits(0))).to(equal([]))

  with it('returns 1 value for powers of 2'):
    for x in range(8):
      expect(list(bloom_mask.bits(2**x))).to(have_len(1))

  with it('returns values in ascending order'):
    result = list(bloom_mask.bits(0b11111111))
    for a, b in zip(result, result[1:]):
      expect(a).to(be_below(b))

  with it('returns matching values'):
    expect(list(bloom_mask.bits(0b101))).to(equal([
      0b001,
      0b100,
    ]))


with description('lengths_product'):
  with it('returns 0 if either argument is 0'):
    for a, b in ((0b1, 0b0), (0b0, 0b1)):
      expect(calling(bloom_mask.lengths_product, a, b)).to(equal(0b0))

  with it('returns other value if either argument is 1'):
    for a, b in ((0b1, 0b1), (0b1, 0b10), (0b1, 0b100), (0b1, 0b1000)):
      expect(calling(bloom_mask.lengths_product, a, b)).to(equal(a * b))

  with it('returns product if both arguments are only 1 bit'):
    for a, b in ((0b10, 0b10), (0b10, 0b100), (0b10, 0b1000)):
      expect(calling(bloom_mask.lengths_product, a, b)).to(equal(a * b))

  with it('shifts input if either argument is 1 bit'):
    for a, b in ((0b1010, 0b10), (0b1111, 0b100), (0b1011, 0b1000)):
      expect(calling(bloom_mask.lengths_product, a, b)).to(equal(a * b))

  with it('handles more complex bitfields'):
    expect(bin(bloom_mask.lengths_product(0b10101, 0b101))).to(
        equal('0b1010101'))
    expect(bin(bloom_mask.lengths_product(0b100001, 0b101))).to(
        equal('0b10100101'))
    expect(bin(bloom_mask.lengths_product(0b111, 0b101))).to(equal('0b11111'))

  with it('duplicates make second argument much larger'):
    for duplicates in range(1, 12):
      expect(
          calling(bloom_mask.lengths_product, 1, 2, duplicates=duplicates)
      ).to(equal(2 ** duplicates))


with description('for_alpha'):
  with it('raises for bad input'):
    expect(calling(bloom_mask.for_alpha, 'word')).to(raise_error(ValueError))
    expect(calling(bloom_mask.for_alpha, '123')).to(raise_error(ValueError))

  with it('raises for unsupported input'):
    expect(calling(bloom_mask.for_alpha, '#')).to(
        raise_error(NotImplementedError))
    expect(calling(bloom_mask.for_alpha, '$')).to(
        raise_error(NotImplementedError))

  with it('produces increasing unique values'):
    seen = 0
    last = -1
    for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\'':
      expect(call(bloom_mask.for_alpha, c)).to(be_above(last))
      last = bloom_mask.for_alpha(c)
      expect(last & seen).to(equal(0))
      seen |= last


with description('map_to_str'):
  with it('produces no output for 0s'):
    expect(bloom_mask.map_to_str(0, 0)).to(equal(''))

  with it('indicates provided characters'):
    expect(bloom_mask.map_to_str(0b111, 0)).to(equal('abc'))

  with it('indicates required characters differently'):
    expect(bloom_mask.map_to_str(0b111, 0b111)).to(equal('ABC'))

  with it('indicates PROVIDE_NOTHING as 0'):
    expect(bloom_mask.map_to_str(bloom_mask.PROVIDE_NOTHING, 0)).to(equal(''))

  with it('indicates PROVIDE_NOTHING+REQUIRE_NOTHING as 0'):
    expect(bloom_mask.map_to_str(
        bloom_mask.PROVIDE_NOTHING, bloom_mask.REQUIRE_NOTHING)).to(equal(''))

  with it('converts roundtrip'):
    expect(bloom_mask.map_to_str(
        bloom_mask.for_alpha('i') |
        bloom_mask.for_alpha('t') |
        bloom_mask.for_alpha("'") |
        bloom_mask.for_alpha('s') |
        bloom_mask.for_alpha(' ') |
        bloom_mask.for_alpha('a') |
        bloom_mask.for_alpha(' ') |
        bloom_mask.for_alpha('T') |
        bloom_mask.for_alpha('E') |
        bloom_mask.for_alpha('S') |
        bloom_mask.for_alpha('T'), 0)).to(equal("aist; ';EST"))


with description('mask defaults') as self:
  with before.each:
    self.subject = bloom_mask.BitMatchAnything()

  with it('is 0 initially'):
    expect(self.subject).to(equal(0))

  with it('bitwise ORs to itself'):
    expect(self.subject | 0b101).to(be(0b101))

  with it('bitwise ANDs to itself'):
    expect(self.subject & 0b101).to(be(0b101))

  with it('bitwise ANDs & assigns to itself'):
    self.subject &= 0b101
    expect(self.subject).to(be(0b101))

  with it('bitwise rORs to other'):
    expect(0b101 | self.subject).to(be(0b101))

  with it('bitwise rANDs to other'):
    expect(0b101 & self.subject).to(be(0b101))

  with it('bitwise rANDs & assigns to other'):
    x = 0b101
    x &= self.subject
    expect(x).to(be(0b101))

  with it('claims equality'):
    expect(0b101 & 0b0).to(equal(self.subject))

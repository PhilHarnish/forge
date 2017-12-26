from data.graph import bloom_mask
from spec.mamba import *


with description('for_alpha'):
  with it('raises for bad input'):
    expect(calling(bloom_mask.for_alpha, 'word')).to(raise_error(ValueError))
    expect(calling(bloom_mask.for_alpha, '123')).to(raise_error(ValueError))

  with it('raises for unsupported input'):
    expect(calling(bloom_mask.for_alpha, '#')).to(
        raise_error(NotImplementedError))
    expect(calling(bloom_mask.for_alpha, '$')).to(
        raise_error(NotImplementedError))
    expect(calling(bloom_mask.for_alpha, ' ')).to(
        raise_error(NotImplementedError))

  with it('produces increasing unique values'):
    seen = 0
    last = -1
    for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
      expect(call(bloom_mask.for_alpha, c)).to(be_above(last))
      last = bloom_mask.for_alpha(c)
      expect(last & seen).to(equal(0))
      seen |= last


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

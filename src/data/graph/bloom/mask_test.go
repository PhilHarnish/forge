package bloom_test

import (
	"strings"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom"
)

var _ = Describe("AlphabetMask",
	func() {
		It("Accepts all characters from ALPHABET",
			func() {
				for _, c := range bloom.ALPHABET {
					_, err := bloom.AlphabetMask(c)
					Expect(err).ShouldNot(HaveOccurred())
				}
			})

		It("Rejects characters outside of ALPHABET",
			func() {
				invalidCharacters := 0
				for i := 0; i < 200; i++ {
					c := rune(i)
					if strings.ContainsRune(bloom.ALPHABET, c) {
						continue
					}
					invalidCharacters++
					_, err := bloom.AlphabetMask(c)
					Expect(err).NotTo(BeNil())
				}
				Expect(invalidCharacters).To(BeNumerically(">", 0))
			})

		It("Returns unique masks for each character",
			func() {
				acc := bloom.BitMask(0)
				for _, c := range bloom.ALPHABET {
					mask, _ := bloom.AlphabetMask(c)
					Expect(mask).To(BeNumerically(">", 0))
					Expect(acc & mask).To(Equal(bloom.BitMask(0)))
					acc |= mask
				}
			})
	})

/*
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
    for c in 'abcdefghijklmnopqrstuvwxyz \'':
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
        bloom_mask.for_alpha('t') |
        bloom_mask.for_alpha('e') |
        bloom_mask.for_alpha('s') |
        bloom_mask.for_alpha('t'), 0)).to(equal("aeist; '"))


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

*/

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

var _ = Describe("MaskAlphabet",
	func() {
		It("Returns empty string for 0",
			func() {
				Expect(bloom.MaskAlphabet(0b0, 0b0)).To(Equal(""))
			})

		It("Indicates provided characters",
			func() {
				Expect(bloom.MaskAlphabet(0b111, 0)).To(Equal("abc"))
			})

		It("Indicates required characters differently",
			func() {
				Expect(bloom.MaskAlphabet(0b111, 0b111)).To(Equal("ABC"))
			})

		It("Converts round-trip",
			func() {
				given := "it's an example"
				expected := "aeilmnpstx '"
				acc := bloom.BitMask(0)
				for _, c := range given {
					mask, _ := bloom.AlphabetMask(c)
					acc |= mask
				}
				Expect(bloom.MaskAlphabet(acc, 0)).To(Equal(expected))
			})
	})

/*


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

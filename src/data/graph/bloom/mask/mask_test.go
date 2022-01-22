package mask_test

import (
	"strings"
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
)

func TestMask(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Mask tests")
}

var _ = Describe("Position",
	func() {
		It("Accepts all characters from ALPHABET",
			func() {
				for _, c := range mask.ALPHABET {
					_, err := mask.Position(c)
					Expect(err).ShouldNot(HaveOccurred())
				}
			})

		It("Rejects characters outside of ALPHABET",
			func() {
				invalidCharacters := 0
				for i := 0; i < 200; i++ {
					c := rune(i)
					if strings.ContainsRune(mask.ALPHABET, c) {
						continue
					}
					invalidCharacters++
					_, err := mask.Position(c)
					Expect(err).NotTo(BeNil())
				}
				Expect(invalidCharacters).To(BeNumerically(">", 0))
			})

		It("Returns increasing values for each character",
			func() {
				last := -1
				for _, c := range mask.ALPHABET {
					position, _ := mask.Position(c)
					Expect(position).To(BeNumerically(">", last))
					last = position
				}
			})
	})

var _ = Describe("AlphabetMask",
	func() {
		It("Accepts all characters from ALPHABET",
			func() {
				for _, c := range mask.ALPHABET {
					_, err := mask.AlphabetMask(c)
					Expect(err).ShouldNot(HaveOccurred())
				}
			})

		It("Rejects characters outside of ALPHABET",
			func() {
				invalidCharacters := 0
				for i := 0; i < 200; i++ {
					c := rune(i)
					if strings.ContainsRune(mask.ALPHABET, c) {
						continue
					}
					invalidCharacters++
					_, err := mask.AlphabetMask(c)
					Expect(err).NotTo(BeNil())
				}
				Expect(invalidCharacters).To(BeNumerically(">", 0))
			})

		It("Returns unique masks for each character",
			func() {
				acc := mask.Mask(0)
				for _, c := range mask.ALPHABET {
					m, _ := mask.AlphabetMask(c)
					Expect(m).To(BeNumerically(">", 0))
					Expect(acc & m).To(Equal(mask.Mask(0)))
					acc |= m
				}
			})
	})

var _ = Describe("MaskAlphabet",
	func() {
		It("Returns empty string for 0",
			func() {
				Expect(mask.MaskAlphabet(0b0, 0b0)).To(Equal(""))
			})

		It("Indicates provided characters",
			func() {
				Expect(mask.MaskAlphabet(0b111, 0)).To(Equal("abc"))
			})

		It("Indicates required characters differently",
			func() {
				Expect(mask.MaskAlphabet(0b111, 0b111)).To(Equal("ABC"))
			})

		It("Converts round-trip",
			func() {
				given := "it's an example"
				expected := "aeilmnpstx '"
				acc := mask.Mask(0)
				for _, c := range given {
					mask, _ := mask.AlphabetMask(c)
					acc |= mask
				}
				Expect(mask.MaskAlphabet(acc, 0)).To(Equal(expected))
			})

		It("Converts ALL to ALPHABET",
			func() {
				Expect(mask.MaskAlphabet(mask.ALL, 0)).To(Equal(mask.ALPHABET))
			})

		It("Is not fooled by UNSET",
			func() {
				Expect(mask.MaskAlphabet(mask.ALL, mask.UNSET)).To(Equal(mask.ALPHABET))
			})
	})

var _ = Describe("LengthAlphabet",
	func() {
		It("Returns empty string for 0",
			func() {
				Expect(mask.LengthAlphabet(0b0)).To(Equal(""))
			})

		It("Indicates matching lengths",
			func() {
				Expect(mask.LengthAlphabet(0b1011)).To(Equal("## #"))
			})
	})

var _ = Describe("Default masks",
	func() {
		It("NONE is matches none of ALPHABET",
			func() {
				for _, c := range mask.ALPHABET {
					m, _ := mask.AlphabetMask(c)
					Expect(m & mask.NONE).To(Equal(mask.Mask(0)))
				}
			})

		It("ALL is matches all of ALPHABET",
			func() {
				for _, c := range mask.ALPHABET {
					m, _ := mask.AlphabetMask(c)
					Expect(m & mask.ALL).NotTo(Equal(mask.Mask(0)))
				}
			})
	})

package bloom_test

import (
	"strings"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom"
)

var _ = Describe("Position",
	func() {
		It("Accepts all characters from ALPHABET",
			func() {
				for _, c := range bloom.ALPHABET {
					_, err := bloom.Position(c)
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
					_, err := bloom.Position(c)
					Expect(err).NotTo(BeNil())
				}
				Expect(invalidCharacters).To(BeNumerically(">", 0))
			})

		It("Returns increasing values for each character",
			func() {
				last := -1
				for _, c := range bloom.ALPHABET {
					position, _ := bloom.Position(c)
					Expect(position).To(BeNumerically(">", last))
					last = position
				}
			})
	})

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

		It("Converts ALL to ALPHABET",
			func() {
				Expect(bloom.MaskAlphabet(bloom.ALL, 0)).To(Equal(bloom.ALPHABET))
			})

		It("Is not fooled by UNSET",
			func() {
				Expect(bloom.MaskAlphabet(bloom.ALL, bloom.UNSET)).To(Equal(bloom.ALPHABET))
			})
	})

var _ = Describe("LengthAlphabet",
	func() {
		It("Returns empty string for 0",
			func() {
				Expect(bloom.LengthAlphabet(0b0)).To(Equal(""))
			})

		It("Indicates matching lengths",
			func() {
				Expect(bloom.LengthAlphabet(0b1011)).To(Equal("## #"))
			})
	})

var _ = Describe("Default masks",
	func() {
		It("NONE is matches none of ALPHABET",
			func() {
				for _, c := range bloom.ALPHABET {
					mask, _ := bloom.AlphabetMask(c)
					Expect(mask & bloom.NONE).To(Equal(bloom.BitMask(0)))
				}
			})

		It("ALL is matches all of ALPHABET",
			func() {
				for _, c := range bloom.ALPHABET {
					mask, _ := bloom.AlphabetMask(c)
					Expect(mask & bloom.ALL).NotTo(Equal(bloom.BitMask(0)))
				}
			})
	})
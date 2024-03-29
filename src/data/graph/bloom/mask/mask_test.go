package mask_test

import (
	"strings"
	"testing"
	"unicode"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
)

func TestMask(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Mask tests")
}

var _ = Describe("Default masks", func() {
	It("NONE is matches none of ALPHABET", func() {
		for _, c := range mask.ALPHABET {
			m, _ := mask.AlphabetMask(c)
			Expect(m & mask.NONE).To(Equal(mask.Mask(0)))
		}
	})

	It("ALL is matches all of ALPHABET", func() {
		for _, c := range mask.ALPHABET {
			m, _ := mask.AlphabetMask(c)
			Expect(m & mask.ALL).NotTo(Equal(mask.Mask(0)))
		}
	})

	It("sets AlphabetRuneRanges to all ranges", func() {
		Expect(mask.AlphabetRuneRanges).To(Equal([]rune{
			' ', ' ',
			'\'', '\'',
			'-', '-',
			'a', 'z',
		}))
	})
})

var _ = Describe("Position", func() {
	It("Accepts all characters from ALPHABET", func() {
		for _, c := range mask.ALPHABET {
			_, err := mask.Position(c)
			Expect(err).ShouldNot(HaveOccurred())
		}
	})

	It("Rejects characters outside of ALPHABET", func() {
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

	It("Returns increasing values for each character", func() {
		last := -1
		for _, c := range mask.ALPHABET {
			position, _ := mask.Position(c)
			Expect(position).To(BeNumerically(">", last))
			last = position
		}
	})
})

var _ = Describe("AlphabetMask", func() {
	It("Accepts all characters from ALPHABET", func() {
		for _, c := range mask.ALPHABET {
			_, err := mask.AlphabetMask(c)
			Expect(err).ShouldNot(HaveOccurred())
		}
	})

	It("Rejects characters outside of ALPHABET", func() {
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

	It("Returns unique masks for each character", func() {
		acc := mask.Mask(0)
		for _, c := range mask.ALPHABET {
			m, _ := mask.AlphabetMask(c)
			Expect(m).To(BeNumerically(">", 0))
			Expect(acc & m).To(Equal(mask.Mask(0)))
			acc |= m
		}
	})
})

var _ = Describe("AlphabetMaskRange", func() {
	It("Accepts a range of width zero", func() {
		result, err := mask.AlphabetMaskRange('a', 'a')
		Expect(err).NotTo(HaveOccurred())
		Expect(result).To(Equal(mask.Mask(0b1)))
	})

	It("Accepts a range of several characters", func() {
		result, err := mask.AlphabetMaskRange('a', 'c')
		Expect(err).NotTo(HaveOccurred())
		Expect(result).To(Equal(mask.Mask(0b111)))
	})

	It("Rejects invalid input", func() {
		_, err := mask.AlphabetMaskRange('🚫', 'b')
		Expect(err).To(HaveOccurred())
		_, err = mask.AlphabetMaskRange('a', '🚫')
		Expect(err).To(HaveOccurred())
	})

	It("Rejects invalid range", func() {
		_, err := mask.AlphabetMaskRange('a', ' ')
		Expect(err).To(HaveOccurred())
	})
})

var _ = Describe("AlphabetMaskRanges", func() {
	It("Accepts empty set", func() {
		result, err := mask.AlphabetMaskRanges([]rune{})
		Expect(err).NotTo(HaveOccurred())
		Expect(result).To(Equal(mask.NONE))
	})

	It("Accepts a range of several characters", func() {
		result, err := mask.AlphabetMaskRanges([]rune{'a', 'c'})
		Expect(err).NotTo(HaveOccurred())
		Expect(result).To(Equal(mask.Mask(0b111)))
	})

	It("Accepts sets of characters", func() {
		result, err := mask.AlphabetMaskRanges([]rune{'a', 'c', 'e', 'g'})
		Expect(err).NotTo(HaveOccurred())
		Expect(result).To(Equal(mask.Mask(0b1110111)))
	})

	It("Accepts full set of characters", func() {
		result, err := mask.AlphabetMaskRanges(mask.AlphabetRuneRanges)
		Expect(err).NotTo(HaveOccurred())
		Expect(result).To(Equal(mask.ALL))
	})

	It("Rejects invalid input", func() {
		_, err := mask.AlphabetMaskRanges([]rune{'a', '🚫'})
		Expect(err).To(HaveOccurred())
	})

	It("Rejects invalid length", func() {
		_, err := mask.AlphabetMaskRanges([]rune{'a'})
		Expect(err).To(HaveOccurred())
	})

	It("Rejects invalid range", func() {
		_, err := mask.AlphabetMaskRanges([]rune{'a', ' '})
		Expect(err).To(HaveOccurred())
	})
})

var _ = Describe("AlphabetMasks", func() {
	It("Starts empty, initially", func() {
		masks, err := mask.AlphabetMasks(nil)
		Expect(err).NotTo(HaveOccurred())
		Expect(masks).To(HaveLen(0))
	})

	It("Handles one character", func() {
		masks, err := mask.AlphabetMasks([]rune{'a'})
		Expect(err).NotTo(HaveOccurred())
		Expect(masks).To(HaveLen(1))
		Expect(masks[0]).To(Equal(mask.Mask(0b1)))
	})

	It("Handles many characters", func() {
		masks, err := mask.AlphabetMasks([]rune{'a', 'b', 'c'})
		Expect(err).NotTo(HaveOccurred())
		Expect(masks).To(HaveLen(3))
		Expect(masks[0]).To(Equal(mask.Mask(0b111)))
		Expect(masks[1]).To(Equal(mask.Mask(0b110)))
		Expect(masks[2]).To(Equal(mask.Mask(0b100)))
	})

	It("Handles errors", func() {
		_, err := mask.AlphabetMasks([]rune{'a', 'b', '🚫'})
		Expect(err).To(HaveOccurred())
	})
})

var _ = Describe("ClampRunes", func() {
	It("is a no-op for empty input", func() {
		clamped := mask.ClampRunes(nil)
		Expect(clamped).To(HaveLen(0))
	})

	It("returns everything for full range", func() {
		clamped := mask.ClampRunes([]rune{0, unicode.MaxRune})
		Expect(clamped).To(Equal(mask.AlphabetRuneRanges))
	})

	It("returns nothing for invalid ranges", func() {
		clamped := mask.ClampRunes([]rune{'A', 'Z'})
		Expect(clamped).To(HaveLen(0))
	})

	It("returns subset for overlaps", func() {
		clamped := mask.ClampRunes([]rune{'A', 'c', 'x', 'z'})
		Expect(clamped).To(Equal([]rune{'a', 'c', 'x', 'z'}))
	})
})

var _ = Describe("EdgeMask", func() {
	It("Starts empty, initially", func() {
		edge, err := mask.EdgeMask("")
		Expect(err).NotTo(HaveOccurred())
		Expect(edge).To(Equal(mask.Mask(0b0)))
	})

	It("Handles one character", func() {
		edge, err := mask.EdgeMask("a")
		Expect(err).NotTo(HaveOccurred())
		Expect(edge).To(Equal(mask.Mask(0b1)))
	})

	It("Handles many characters", func() {
		edge, err := mask.EdgeMask("abc")
		Expect(err).NotTo(HaveOccurred())
		Expect(edge).To(Equal(mask.Mask(0b111)))
	})

	It("Detects invalid characters", func() {
		_, err := mask.EdgeMask("abc🚫")
		Expect(err).To(HaveOccurred())
	})
})

var _ = Describe("EdgeMaskAndLength", func() {
	It("Starts empty, initially", func() {
		edge, length, err := mask.EdgeMaskAndLength("")
		Expect(err).NotTo(HaveOccurred())
		Expect(edge).To(Equal(mask.Mask(0b0)))
		Expect(length).To(Equal(0))
	})

	It("Handles one character", func() {
		edge, length, err := mask.EdgeMaskAndLength("a")
		Expect(err).NotTo(HaveOccurred())
		Expect(edge).To(Equal(mask.Mask(0b1)))
		Expect(length).To(Equal(1))
	})

	It("Handles many characters", func() {
		edge, length, err := mask.EdgeMaskAndLength("abc")
		Expect(err).NotTo(HaveOccurred())
		Expect(edge).To(Equal(mask.Mask(0b111)))
		Expect(length).To(Equal(3))
	})

	It("Detects invalid characters", func() {
		_, _, err := mask.EdgeMaskAndLength("abc🚫")
		Expect(err).To(HaveOccurred())
	})
})

var _ = Describe("LengthString", func() {
	It("Returns empty string for 0", func() {
		Expect(mask.LengthString(0b0)).To(Equal(""))
	})

	It("Indicates matching lengths", func() {
		Expect(mask.LengthString(0b1011)).To(Equal("●●◌●"))
	})

	It("Indicates when ALL_REMAINING_LENGTH is set", func() {
		Expect(mask.LengthString(mask.Mask(0b101 | mask.ALL_REMAINING_LENGTH))).To(Equal(
			"●◌●◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌◌●···"))
	})

	It("Truncates when the end is all 1s", func() {
		lengthMask := mask.ALL_LENGTHS | mask.ALL_REMAINING_LENGTH
		Expect(mask.LengthString(lengthMask)).To(Equal("●●●···"))
		lengthMask -= mask.Mask(0b110101)
		Expect(mask.LengthString(lengthMask)).To(Equal("◌●◌●◌◌●●●···"))
	})
})

var _ = Describe("MaskString", func() {
	It("Returns empty string for 0", func() {
		Expect(mask.MaskString(0b0, 0b0)).To(Equal(""))
	})

	It("Indicates provided characters", func() {
		Expect(mask.MaskString(0b111, 0)).To(Equal("abc"))
	})

	It("Indicates all provided characters", func() {
		Expect(mask.MaskString(mask.ALL, 0)).To(Equal(
			"abcdefghijklmnopqrstuvwxyz␣-'"))
	})

	It("Indicates required characters differently", func() {
		Expect(mask.MaskString(0b111, 0b111)).To(Equal("ABC"))
	})

	It("Indicates all required characters", func() {
		Expect(mask.MaskString(mask.ALL, mask.ALL)).To(Equal(
			"ABCDEFGHIJKLMNOPQRSTUVWXYZ␣-'"))
	})

	It("Indicates unsatisfied characters differently", func() {
		Expect(mask.MaskString(0b000, mask.ALL)).To(Equal(
			"ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ( )(-)(')"))
	})

	It("Converts round-trip", func() {
		given := "aeilmnpstx '"
		acc := mask.Mask(0)
		for _, c := range given {
			mask, _ := mask.AlphabetMask(c)
			acc |= mask
		}
		Expect(mask.MaskString(acc, 0)).To(Equal(
			strings.ReplaceAll(given, " ", "␣")))
	})

	It("Converts ALL to ALPHABET", func() {
		Expect(mask.MaskString(mask.ALL, 0)).To(Equal(
			strings.ReplaceAll(mask.ALPHABET, " ", "␣")))
	})

	It("Is not fooled by UNSET", func() {
		Expect(mask.MaskString(mask.ALL, mask.UNSET)).To(Equal(
			strings.ReplaceAll(mask.ALPHABET, " ", "␣")))
	})
})

var _ = Describe("ConcatLengths", func() {
	It("Returns zeros out for zeros in", func() {
		Expect(mask.LengthString(mask.ConcatLengths(0b0, 0b0))).To(Equal(
			""))
	})

	It("Returns one for ones in", func() {
		Expect(mask.LengthString(mask.ConcatLengths(0b1, 0b1))).To(Equal(
			"●"))
	})

	It("Returns shifted input for twos", func() {
		Expect(mask.LengthString(mask.ConcatLengths(0b10, 0b10))).To(Equal(
			"◌◌●"))
	})

	It("Mirrors input for multiples", func() {
		first := mask.Mask((1 << 3) | (1 << 5))
		second := mask.Mask((1 << 7) | (1 << 11))
		expected := mask.Mask(
			(1<<3)*(1<<7) |
				(1<<3)*(1<<11) |
				(1<<5)*(1<<7) |
				(1<<5)*(1<<11))
		Expect(mask.LengthString(mask.ConcatLengths(first, second))).To(Equal(
			mask.LengthString(expected)))
	})

	It("Handles (a, repeats)", func() {
		a := mask.Mask(0b10100000000)
		repeats := mask.RepeatLengths(0b100, 4)
		Expect(mask.LengthString(mask.ConcatLengths(a, repeats))).To(Equal(
			"◌◌◌◌◌◌◌◌◌◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●●···"))
	})

	It("Handles (repeats, b)", func() {
		repeats := mask.RepeatLengths(0b100, 4)
		b := mask.Mask(0b10100000000)
		Expect(mask.LengthString(mask.ConcatLengths(repeats, b))).To(Equal(
			"◌◌◌◌◌◌◌◌◌◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●●···"))
	})
})

var _ = Describe("ConcatInfinitely", func() {
	It("Returns zeros out for zeros in", func() {
		Expect(mask.LengthString(mask.ConcatInfinitely(0b0))).To(Equal(
			""))
	})

	It("Handles self-only (identity)", func() {
		Expect(mask.LengthString(mask.ConcatInfinitely(0b1))).To(Equal(
			"●"))
	})

	It("Handles shifted values", func() {
		Expect(mask.LengthString(mask.ConcatInfinitely(0b100))).To(Equal(
			"◌◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●●···"))
	})

	It("Handles combination of self + shift", func() {
		Expect(mask.LengthString(mask.ConcatInfinitely(0b101))).To(Equal(
			"●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●●···"))
	})

	It("Eventually sets all high bits", func() {
		Expect(mask.LengthString(mask.ConcatInfinitely(0b110101))).To(Equal(
			"●◌●◌●●●···"))
	})
})

var _ = Describe("RepeatLengths", func() {
	It("Blurs bits when interval is 1", func() {
		Expect(mask.LengthString(mask.RepeatLengths(0b100, 1))).To(Equal(
			"◌◌●●●···"))
	})

	It("Repeats pattern when interval is 2+", func() {
		Expect(mask.LengthString(mask.RepeatLengths(0b100, 2))).To(Equal(
			"◌◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●●···"))
	})

	It("Repeats unique pattern with high interval", func() {
		Expect(mask.LengthString(mask.RepeatLengths(0b1101, 7))).To(Equal(
			"●◌●●◌◌◌●◌●●◌◌◌●◌●●◌◌◌●◌●●◌◌◌●◌●●◌◌◌●◌●●◌◌◌●◌●●◌◌◌●◌●●◌◌◌●◌●●◌◌◌●···"))
	})

	It("Panics for invalid input", func() {
		Expect(func() {
			mask.RepeatLengths(0b100, -1)
		}).To(PanicWith("Invalid RepeatLengths interval: -1"))
	})
})

var _ = Describe("ShiftLength", func() {
	It("Is a no-op for zero shift", func() {
		Expect(mask.ShiftLength(0b111, 0)).To(Equal(mask.Mask(0b111)))
	})

	It("shifts simple numbers", func() {
		Expect(mask.ShiftLength(0b111, 3)).To(Equal(mask.Mask(0b111000)))
	})

	It("preserves the ALL_REMAINING_LENGTH bit", func() {
		given := mask.Mask(0b111 | mask.ALL_REMAINING_LENGTH)
		Expect(mask.ShiftLength(given, 3)).To(Equal(mask.Mask(0b111000 | mask.ALL_REMAINING_LENGTH)))
	})
})

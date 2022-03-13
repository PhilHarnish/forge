package mask

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"unicode"
)

type Mask = uint64

const (
	LETTERS   = "abcdefghijklmnopqrstuvwxyz"
	SEPARATOR = " -"
	EXTRA     = "'"
	ALPHABET  = LETTERS + SEPARATOR + EXTRA
	SIZE      = len(ALPHABET)
	ALL       = Mask((1 << SIZE) - 1)
	NONE      = Mask(0b0)
	// NB: Unset is all 1s so that require is iteratively less over time.
	UNSET         = Mask(1<<SIZE) | ALL
	VALID_LENGTHS = Mask((1 << 63) - 1)
	// This bit indicates the end has been reached.
	ALL_REMAINING_LENGTH = Mask(1 << 63)
	ALL_LENGTHS          = (ALL_REMAINING_LENGTH - 1) | ALL_REMAINING_LENGTH
)

var AlphabetRuneRanges = collectRuneRanges([]rune(ALPHABET))

var missingRequirementMap = [...]rune{
	'Ⓐ', 'Ⓑ', 'Ⓒ', 'Ⓓ', 'Ⓔ', 'Ⓕ', 'Ⓖ', 'Ⓗ', 'Ⓘ', 'Ⓙ', 'Ⓚ', 'Ⓛ', 'Ⓜ',
	'Ⓝ', 'Ⓞ', 'Ⓟ', 'Ⓠ', 'Ⓡ', 'Ⓢ', 'Ⓣ', 'Ⓤ', 'Ⓥ', 'Ⓦ', 'Ⓧ', 'Ⓨ', 'Ⓩ',
}

var truncateLengths = regexp.MustCompile("●{5,}$")

/*
Returns the position for the given rune if supported, otherwise error.
*/
func Position(c rune) (int, error) {
	if 'a' <= c && c <= 'z' {
		return int(c - 'a'), nil
	} else if c == ' ' {
		return len(LETTERS), nil
	} else if c == '-' {
		return len(LETTERS) + 1, nil
	} else if c == '\'' {
		return len(LETTERS) + 2, nil
	}
	return 0, fmt.Errorf("%q not supported", c)
}

/*
Returns a BitMask for the given rune if supported, otherwise error.
*/
func AlphabetMask(c rune) (Mask, error) {
	position, err := Position(c)
	if err != nil {
		return 0, err
	}
	return 1 << position, nil
}

/*
Returns a BitMask for all runes between start and error, otherwise error.
*/
func AlphabetMaskRange(start rune, end rune) (Mask, error) {
	startPosition, err := Position(start)
	if err != nil {
		return 0, err
	}
	endPosition, err := Position(end)
	if err != nil {
		return 0, err
	}
	delta := int(end - start)
	// Assume positions are contiguous.
	if delta != endPosition-startPosition {
		return 0, fmt.Errorf("AlphabetMaskRange only supports contiguous ranges")
	}
	upperBits := (1 << (endPosition + 1)) - 1
	lowerBits := (1 << startPosition) - 1

	return uint64(upperBits - lowerBits), nil
}

/*
Return a Mask which combines the ranges from pairs of runes.
*/
func AlphabetMaskRanges(runes []rune) (Mask, error) {
	if len(runes)%2 != 0 {
		return NONE, fmt.Errorf("odd number of runes provided: %v", runes)
	}
	result := Mask(0)
	for i := 0; i < len(runes); i += 2 {
		mask, err := AlphabetMaskRange(runes[i], runes[i+1])
		result |= mask
		if err != nil {
			return NONE, err
		}
	}
	return result, nil
}

/*
Returns a slice of BitMasks which match required runes.
Earlier BitMasks assume all later BitMasks also apply.
*/
func AlphabetMasks(runes []rune) ([]Mask, error) {
	// Preprocess path to determine the requirements along path.
	requirements := make([]Mask, len(runes))
	required := Mask(0)
	for i := len(runes) - 1; i >= 0; i-- {
		mask, err := AlphabetMask(runes[i])
		if err != nil {
			return nil, err
		}
		required |= mask
		requirements[i] = required
	}
	return requirements, nil
}

/*
Returns a BitMask for the given edge if supported, otherwise error.
*/
func EdgeMask(edge string) (Mask, error) {
	edgeMask, _, err := EdgeMaskAndLength(edge)
	return edgeMask, err
}

/*
Returns a BitMask for the given edge if supported, otherwise error.
*/
func EdgeMaskAndLength(edge string) (Mask, int, error) {
	edgeMask := Mask(0)
	if len(edge) == 0 {
		return edgeMask, 0, nil
	}
	var c rune
	var length int
	for length, c = range edge {
		mask, err := AlphabetMask(c)
		if err != nil {
			return Mask(0), 0, err
		}
		edgeMask |= mask
	}
	return edgeMask, length + 1, nil
}

/*
Converts lengths mask to a human-readable string.
*/
func LengthString(lengthMask Mask) string {
	if lengthMask == 0 {
		return ""
	}
	hasAllRemainingBit := lengthMask&ALL_REMAINING_LENGTH != 0
	binary := strconv.FormatUint(lengthMask, 2)
	result := strings.Builder{}
	for i := len(binary) - 1; i >= 0; i-- {
		if binary[i] == '0' {
			result.WriteRune('◌')
		} else {
			result.WriteRune('●')
		}
	}
	combined := result.String()

	if hasAllRemainingBit {
		if len(binary) == 64 {
			combined = truncateLengths.ReplaceAllLiteralString(result.String(), "●●●")
		}
		combined += "···"
	}
	return combined
}

/*
Converts `provide` & `require` BitMasks to a human-readable string.
*/
func MaskString(provide Mask, require Mask) string {
	acc := strings.Builder{}
	for _, c := range ALPHABET {
		mask, _ := AlphabetMask(c)
		masked := mask & provide
		required := require & masked
		missing := (require & mask) - required
		if require != UNSET && required > 0 {
			acc.WriteRune(unicode.ToUpper(c))
		} else if require != UNSET && missing > 0 {
			position, _ := Position(c)
			if position < len(missingRequirementMap) {
				acc.WriteRune(missingRequirementMap[position])
			} else {
				acc.WriteString(fmt.Sprintf("(%c)", c))
			}
		} else if masked > 0 {
			acc.WriteRune(c)
		}
	}
	return acc.String()
}

/*
Repeats lengthMask into higher bits.
*/
func RepeatLengths(lengthMask Mask, interval int) Mask {
	if interval == 1 {
		// Special case: set all bits above lowest set bit.
		lowestBit := lengthMask & (^lengthMask + 1)
		lowerBitMask := (lowestBit - 1) | ALL_REMAINING_LENGTH
		allBits := (ALL_REMAINING_LENGTH - 1) ^ lowerBitMask
		return allBits
	}
	for interval < 63 {
		lengthMask |= lengthMask << interval
		interval <<= 1
	}
	lengthMask |= ALL_REMAINING_LENGTH
	return lengthMask
}

/*
Shift lengthMask while preserving ALL_REMAINING_LENGTH
*/
func ShiftLength(lengthMask Mask, distance int) Mask {
	// Split apart VALID_LENGTHS and ALL_REMAINING_LENGTH, shift, then restore.
	allRemainingBit := lengthMask & ALL_REMAINING_LENGTH
	return ((lengthMask & VALID_LENGTHS) << distance) | allRemainingBit
}

func collectRuneRanges(runes []rune) []rune {
	result := []rune{}
	start := runes[0]
	last := start
	for _, c := range runes[1:] {
		if c != last+1 {
			result = append(result, start, last)
			start = c
		}
		last = c
	}
	return append(result, start, last)
}

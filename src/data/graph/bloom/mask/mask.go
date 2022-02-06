package mask

import (
	"fmt"
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
	UNSET = Mask(1<<SIZE) | ALL
)

var missingRequirementMap = [...]rune{
	'Ⓐ', 'Ⓑ', 'Ⓒ', 'Ⓓ', 'Ⓔ', 'Ⓕ', 'Ⓖ', 'Ⓗ', 'Ⓘ', 'Ⓙ', 'Ⓚ', 'Ⓛ', 'Ⓜ',
	'Ⓝ', 'Ⓞ', 'Ⓟ', 'Ⓠ', 'Ⓡ', 'Ⓢ', 'Ⓣ', 'Ⓤ', 'Ⓥ', 'Ⓦ', 'Ⓧ', 'Ⓨ', 'Ⓩ',
}

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
Converts lengths mask to a human-readable string.
*/
func LengthString(lengths Mask) string {
	if lengths == 0 {
		return ""
	}
	binary := strconv.FormatUint(lengths, 2)
	result := strings.Builder{}
	for i := len(binary) - 1; i >= 0; i-- {
		if binary[i] == '0' {
			result.WriteByte(' ')
		} else {
			result.WriteByte('#')
		}
	}
	return result.String()
}

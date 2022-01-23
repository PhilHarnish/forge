package mask

import (
	"fmt"
	"strconv"
	"strings"
	"unicode"
)

type Mask = uint64

type MaskIterable uint64

const (
	LETTERS   = "abcdefghijklmnopqrstuvwxyz"
	SEPARATOR = " -"
	EXTRA     = "'"
	ALPHABET  = LETTERS + SEPARATOR + EXTRA
	SIZE      = len(ALPHABET)
	ALL       = Mask((1 << SIZE) - 1)
	NONE      = Mask(0b0)
	UNSET     = Mask(1<<SIZE | ALL)
)

func (mask *MaskIterable) NextBit() Mask {
	value := *mask
	if value == 0 {
		return 0
	}
	next := value & (value - 1)
	*mask = next
	return Mask(value - next)
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
Converts `provide` & `require` BitMasks to a human-readable string.
*/
func MaskAlphabet(provide Mask, require Mask) string {
	acc := ""
	for _, c := range ALPHABET {
		mask, _ := AlphabetMask(c)
		provided := mask & provide
		if require != UNSET && require&provided > 0 {
			acc += string(unicode.ToUpper(c))
		} else if provided > 0 {
			acc += string(c)
		}
	}
	return acc
}

/*
Converts lengths mask to a human-readable string.
*/
func LengthAlphabet(lengths Mask) string {
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

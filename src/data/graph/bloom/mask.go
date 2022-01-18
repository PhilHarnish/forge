package bloom

import (
	"fmt"
	"unicode"
)

type BitMask = uint64

const (
	LETTERS   = "abcdefghijklmnopqrstuvwxyz"
	SEPARATOR = " -"
	EXTRA     = "'"
	ALPHABET  = LETTERS + SEPARATOR + EXTRA
	SIZE      = len(ALPHABET)
	ALL       = BitMask((1 << SIZE) - 1)
	NONE      = BitMask(0b0)
)

/*
Returns a BitMask for the given rune if supported, otherwise error.
*/
func AlphabetMask(c rune) (BitMask, error) {
	if 'a' <= c && c <= 'z' {
		return 1 << uint(c-'a'), nil
	} else if c == ' ' {
		return 1 << len(LETTERS), nil
	} else if c == '-' {
		return 1 << (len(LETTERS) + 1), nil
	} else if c == '\'' {
		return 1 << (len(LETTERS) + 2), nil
	}
	return 0, fmt.Errorf("%q not supported", c)
}

/*
Converts `provide` & `require` BitMasks to a human-readable string.
*/
func MaskAlphabet(provide BitMask, require BitMask) string {
	acc := ""
	for _, c := range ALPHABET {
		mask, _ := AlphabetMask(c)
		if mask&require > 0 {
			acc += string(unicode.ToUpper(c))
		} else if mask&provide > 0 {
			acc += string(c)
		}
	}
	return acc
}

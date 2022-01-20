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
func AlphabetMask(c rune) (BitMask, error) {
	position, err := Position(c)
	if err != nil {
		return 0, err
	}
	return 1 << position, nil
}

/*
Converts `provide` & `require` BitMasks to a human-readable string.
*/
func MaskAlphabet(provide BitMask, require BitMask) string {
	acc := ""
	for _, c := range ALPHABET {
		mask, _ := AlphabetMask(c)
		provided := mask & provide
		if require&provided > 0 {
			acc += string(unicode.ToUpper(c))
		} else if provided > 0 {
			acc += string(c)
		}
	}
	return acc
}

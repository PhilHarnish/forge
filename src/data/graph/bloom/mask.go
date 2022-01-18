package bloom

import (
	"fmt"
)

type BitMask = uint64

const (
	LETTERS   = "abcdefghijklmnopqrstuvwxyz"
	SEPARATOR = " -"
	EXTRA     = "'"
	ALPHABET  = LETTERS + SEPARATOR + EXTRA
	SIZE      = len(ALPHABET)
)

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

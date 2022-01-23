package main

import (
	"fmt"
	"strconv"

	"github.com/philharnish/forge/src/data/bits"
)

func cbindings() {
	for _, i := range []int{0, 1, 3, 5, 21, 30} {
		target := uint32(1 << i)
		result, err := bits.FindFirstSet(target)
		fmt.Printf("Result for %d (%d = %s) is %d (error: %s)\n",
			(i + 1), target, strconv.FormatInt(int64(target), 2), result, err)
	}
}

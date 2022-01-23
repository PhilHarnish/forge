package bits

// #include "findfirstset.c"
import "C"
import (
	"fmt"
)

func FindFirstSet(i uint32) (int, error) {
	//Convert Go ints to C ints
	iC := C.uint(i)

	sum, err := C.findfirstset(iC)
	if err != nil {
		return 0, fmt.Errorf("error calling C function: %w", err)
	}

	//Convert C.int result to Go int
	return int(sum), nil
}

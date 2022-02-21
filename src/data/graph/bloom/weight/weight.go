package weight

import (
	"fmt"
	"math"
)

type Weight = float64

type WeightedString struct {
	Weight Weight
	String string
}

func CumulativeWeight(strings []WeightedString) Weight {
	if len(strings) == 0 {
		return 0.0
	}
	result := 1.0
	for _, item := range strings {
		result *= item.Weight
	}
	return result
}

func String(weight Weight) string {
	return fmt.Sprintf("%g", math.Round(weight*100))
}

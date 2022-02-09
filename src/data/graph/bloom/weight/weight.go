package weight

import (
	"fmt"
	"strings"
)

type Weight = float64

type WeightedString struct {
	Weight Weight
	String string
}

type WeightedStrings struct {
	Weight  Weight
	Strings []string
}

func (ws *WeightedStrings) String() string {
	var joined string
	if len(ws.Strings) == 0 {
		joined = "∅"
	} else {
		joined = strings.Join(ws.Strings, "\t")
	}
	return fmt.Sprintf("%.2f\t%s", ws.Weight, joined)
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

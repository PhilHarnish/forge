package weight

import (
	"fmt"
	"strings"
)

type Weight = float64

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

package weight

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

package go_euler

func Problem5(n int) int {
	// Create a slice of factors matching [0, n].
	// minFactors[3] == 2 indicates the solution has 3 as a factor twice.
	minFactors := make([]int, n+1)
	for i := 2; i <= n; i++ {
		// Factor creates a channel that returns factors in sort order.
		// We can assume and count 2, 2, 2, 3, 3, 5 as [0, 0, 3, 2, 0, 1].
		factors := Factor(i)
		digit := 0
		count := 0
		for v := range factors {
			if v != digit {
				// Digit changed. Record and reset counter.
				if count > minFactors[digit] {
					minFactors[digit] = count
				}
				digit = v
				count = 1
			} else {
				count++
			}
		}
		// Digit changed. Record and reset counter.
		if count > minFactors[digit] {
			minFactors[digit] = count
		}
	}
	// Accumulate result by multiplying factor^maxCount for each factor.
	result := 1
	for i := 2; i <= n; i++ {
		for j := 0; j < minFactors[i]; j++ {
			result *= i
		}
	}
	return result
}

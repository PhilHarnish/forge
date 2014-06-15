package go_euler

func Problem9(n int) int {
	// Product of pythagorean triplet which sums to n.
	// a < b < c, a + b + c = n.
	// For a = 1: 1 + b + c = n -> b^2 ~= c^2 -> b ~= c -> 2b ~= n.
	max := n / 2
	for a := 1; a < max; a++ {
		a2 := a * a
		for b := a + 1; b < max; b++ {
			c := n - a - b
			if a2+b*b == c*c {
				return a * b * c
			}
		}
	}
	return 0
}

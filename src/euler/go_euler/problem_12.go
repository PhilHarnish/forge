package go_euler

func Problem12(n int) int {
	// First triangle number with 500+ divisors.
	a := 1
	b := 1
	i := 1
	for a*b < n {
		i++
		// The i-th triangle number is i*(i+1)/2.
		// See below for divisor calculation. Since divisors(n) is determined
		// by multiplying count (+1) of prime factors the following applies:
		// divisors(a*b) = divisors(a)*divisors(b) IF a and b do not share primes.
		// divisors(i*(i+1)/2) = divisors2(i)*divisors2(i+1) if divisors2 removes a
		// factor of 2.
		a, b = b, divisorsWithoutFirstTwo(i+1)
	}
	return i * (i + 1) / 2
}

func divisorsWithoutFirstTwo(n int) int {
	// Prime factorization can be used to count divisors.
	// If a number is divisible by 2, 3, 5 then it is also divisible by the
	// different combinations: (2, 3), (2, 5), (3, 5), (2, 3, 5). If a factor
	// appears more than once then duplicates must be
	// discarded. Consider each path for 12 = 2 * 2 * 3:
	// ( 1 ) x ( 1 ) x ( 1 ) -> 1, 3, 2, 6, 2, 6, 4, 12
	// ( 2 )   ( 2 )   ( 3 )
	// With duplicates removed: len(1, 2, 3, 4, 6, 12) = 5. The duplicates are
	// from redundant factors. Instead, (1, 2, 4) x (1, 3) is optimal.
	// So, numDivisors = (count(factor1) + 1) * ... * (count(factorN) + 1)
	if n%2 == 0 {
		n /= 2
	}
	count := 1
	last := 0
	divisors := 1
	for f := range Factor(n) {
		if last != f {
			divisors *= count
			last = f
			count = 2
		} else {
			count++
		}
	}
	// Include the last group.
	return divisors * count
}

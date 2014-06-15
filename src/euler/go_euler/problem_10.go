package go_euler

func Problem10(n int) int {
	// Sum of primes below n.
	f := Primes()
	sum := 0
	for next := <-f; next < n; next = <-f {
		sum += next
	}
	return sum
}

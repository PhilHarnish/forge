package go_euler

func Problem7(n int) int {
	// Nth prime.
	f := Primes()
	return Nth(f, n)
}

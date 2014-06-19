package go_euler

func Problem6(n int) int {
	// Sum square difference.
	// Sum of squares (https://oeis.org/A000330).
	// 1 + 4 + 9 + ... + n^2 = n*(n+1)*(2*n+1)/6
	squareSum := n * (n + 1) * (2*n + 1) / 6
	// Linear sum, squared:
	// 1 + 2 + 3 + 4 + 5 ... n = (n + 1) * (n / 2)
	linearSum := (n + 1) * (n / 2)
	linearSquare := linearSum * linearSum
	difference := linearSquare - squareSum
	return difference
}

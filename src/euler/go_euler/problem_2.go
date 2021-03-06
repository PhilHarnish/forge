package go_euler

// Sum even Fibonacci numbers.
// 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...
// -> 2 + 8 + 34 + ...
func Problem2(ceil int) int {
	sum := 0
	c := Fibonacci()

	next := <-c
	for next < ceil {
		if next%2 == 0 {
			sum += next
		}
		next = <-c
	}

	return sum
}

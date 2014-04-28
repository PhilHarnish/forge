package go_euler

func Factor(n int) func() int {
	exhausted := false
	return func() int {
		if exhausted {
			return 0
		}
		for i := 2; i <= n; i++ {
			if n%i == 0 {
				n /= i
				return i
			}
		}
		exhausted = true
		return 0
	}
}

func Fibonacci() func() int {
	// 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...
	last := 0
	next := 1
	return func() int {
		last, next = next, last+next
		return next
	}
}

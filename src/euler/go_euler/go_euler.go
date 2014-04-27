package go_euler

func Fibonacci() func() int {
	// 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...
	last := 0
	next := 1
	return func() int {
		last, next = next, last+next
		return next
	}
}

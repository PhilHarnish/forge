package go_euler

func Problem3(n int) int {
	c := Factor(n)
	last, next := 0, <-c
	for next != 0 {
		last, next = next, <-c
	}
	return last
}

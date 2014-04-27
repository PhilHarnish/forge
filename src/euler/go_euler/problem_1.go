package go_euler

func Problem1(ceil int, check ...int) int {
	sum := 0
	for i := 0; i < ceil; i++ {
		for _, v := range check {
			if i%v == 0 {
				sum += i
				break
			}
		}
	}
	return sum
}

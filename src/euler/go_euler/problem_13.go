package go_euler

func Problem13(input string, n int) int {
	// Sum a bunch of n-digit numbers and return first 10 digits.
	out := make(chan int)
	pipeline := make([]chan int, n)
	finalDigits := make([]int, n)
	next := out
	for i := 0; i < n; i++ {
		pipeline[i] = make(chan int)
		go p13Sum(pipeline[i], next, &finalDigits[i])
		next = pipeline[i]
	}
	go func() {
		index := 0
		for i := 0; i < len(input); i++ {
			c := int(input[i])
			if c < int('0') || c > int('9') {
				// Ignore newlines.
				index = 0
				continue
			}
			digit := c - int('0')
			pipeline[index] <- digit
			index++
		}
		// Done sending digits to the n-th out channel.
		close(pipeline[n-1])
	}()
	// Finish summing any output to overflow channel.
	overflow := 0
	for i := range out {
		overflow += i
	}
	result := overflow
	size := 2 // Note: not a safe assumption.
	for i := 0; size < 10; i++ {
		result *= 10
		result += finalDigits[i]
		size++
	}
	return result
}

func p13Sum(in, out chan int, final *int) {
	sum := 0
	for i := range in {
		sum += i
		if carry := sum / 10; carry > 0 {
			out <- carry
		}
		sum %= 10
	}
	// Done sending digits to out.
	close(out)
	*final = sum
}

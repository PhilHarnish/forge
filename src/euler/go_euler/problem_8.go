package go_euler

func Problem8(input string, n int) int {
	// Largest n-product in decimal input string.
	largest := 0
	product := 1
	index := 0
	length := 0
	sequence := make([]int, n)
	for i := 0; i < len(input); i++ {
		char := int(input[i])
		if char < int('0') || char > int('9') {
			// Ignore newlines.
			continue
		}
		digit := char - int('0')
		if digit == 0 {
			// Zeros reset all progress.
			length = 0
			index = 0
			product = 1
		} else {
			if length == n {
				// Eject oldest number from sequence.
				product /= sequence[index]
			} else {
				length++
			}
			// (Over)write this digit into circular buffer.
			sequence[index] = digit
			index = (index + 1) % n
			// Calculate new product.
			product *= digit
			if product > largest {
				largest = product
			}
		}
	}
	return largest
}

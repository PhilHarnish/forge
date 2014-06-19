package go_euler

func Problem8(input string, n int) int {
	// Largest n-product in decimal input string.
	return Max(ChainMultiply(strToIntChan(input), n))
}

func strToIntChan(in string) chan int {
	out := make(chan int)
	go strSendToIntChan(in, out)
	return out
}

func strSendToIntChan(in string, out chan int) {
	for i := 0; i < len(in); i++ {
		char := int(in[i])
		if char < int('0') || char > int('9') {
			// Ignore newlines.
			continue
		}
		digit := char - int('0')
		out <- digit
	}
	close(out)
}

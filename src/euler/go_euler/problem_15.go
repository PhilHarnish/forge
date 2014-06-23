package go_euler

func Problem15(n int) int {
	// Paths through an n x n square.
	// 2, 6, 20, 70, 252, 924...
	// A000984: Central binomial coefficients: C(2*n,n) = (2*n)!/(n!)^2.
	// Eg: 12...
	//       24*23*22*21...13*(12*11*10*9*8*7*6*5*4*3*2*1)
	//       ---------------------------------------------
	// (12*11*10*9*8*7*6*5*4*3*2*1) * (12*11*10*9*8*7*6*5*4*3*2*1)

	// 24*23*22*21*20*19*18*17*16*15*14*13
	// -----------------------------------
	//    12*11*10*9*8*7*6*5*4*3*2*1

	// 2*23*2*21*2*19*2*17*2*15*2*13
	// -----------------------------
	//   1*1*1*1*1*1*6*5*4*3*2*1

	// (2n-1)*(2n-2)*...*(n+1)*2^(n/2)
	// -------------------------------
	//             (n/2)!

	numerator := P15Numerator(n)
	denominator := Factorial(n/2)
	return numerator / denominator
}

func P15Numerator(n int) int {
	pow := 1
	for i := 0; i < n/2; i++ {
		pow *= 2
	}
	product := 1
	start := n + 1
	end := 2 * n
	for i := start; i < end; i += 2 {
		product *= i
	}
	return pow * product
}

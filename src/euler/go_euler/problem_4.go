package go_euler

import "math"

func Problem4(numDigits int) int {
	max := int(math.Pow(10, float64(numDigits)))
	largest := 0
	// Looking for largest product that meets specific criteria.
	// Start at max * max, then decrement 1 variable. x >= y at all times.
	for x := max - 1; x > 0; x-- {
		for y := max - 1; y >= x; y-- {
			product := x * y
			if product < largest {
				// Skip remaining y values.
				y = 0
			} else if isPalindrome(product) {
				largest = product
			}
		}
	}
	return largest
}

func isPalindrome(n int) bool {
	// Collect list of digits.
	digits := []int{}
	for n > 0 {
		digits = append(digits, n%10)
		n /= 10
	}
	// Verify each matches.
	for i := 0; i < (len(digits)+1)/2; i++ {
		j := len(digits) - i - 1
		if digits[i] != digits[j] {
			return false
		}
	}
	return true
}

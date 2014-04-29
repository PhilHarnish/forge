package go_euler

import (
	"fmt"
	"github.com/onsi/ginkgo"
)

func Debug(f string, args ...interface{}) {
	fmt.Fprintf(ginkgo.GinkgoWriter, f+"\n", args...)
}

func Factor(n int) chan int {
	c := make(chan int)
	go factor(n, c)
	return c
}

func factor(n int, c chan int) {
	for i := 2; i <= n; i++ {
		if n%i == 0 {
			n /= i
			c <- i
			i = 1 // Repeat loop from beginning.
		}
	}
	close(c)
}

func Fibonacci() chan int {
	c := make(chan int)
	go fibonacci(c)
	return c
}

func fibonacci(c chan int) {
	// 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...
	last, next := 0, 1
	for {
		last, next = next, last+next
		c <- next
	}
}

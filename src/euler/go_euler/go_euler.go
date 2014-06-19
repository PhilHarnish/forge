package go_euler

import (
	"fmt"
	"github.com/onsi/ginkgo"
)

func Debug(args ...interface{}) {
	fmt.Fprintln(ginkgo.GinkgoWriter, args...)
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

func ChainMultiply(in chan int, len int) chan int {
	out := make(chan int)
	go chainMultiply(in, out, len)
	return out
}

func chainMultiply(in chan int, out chan int, len int) {
	product := 1
	chain := make([]int, len)
	chainIndex := 0
	chainLength := 0
	for n := range in {
		if n == 0 {
			chainIndex = 0
			chainLength = 0
			product = 1
		} else {
			if chainLength == len {
				product /= chain[chainIndex]
			} else {
				chainLength++
			}
			chain[chainIndex] = n
			chainIndex = (chainIndex + 1) % len
			product *= n
		}
		out <- product
	}
	close(out)
}

func Max(in chan int) int {
	max := 0
	for n := range in {
		if n > max {
			max = n
		}
	}
	return max
}

func Nth(c chan int, i int) int {
	for ; i > 1; i-- {
		<-c
	}
	return <-c
}

func Primes() chan int {
	// 2, 3, 5, 7, 11, 13, 15...
	c := make(chan int)
	go primes(c)
	return c
}

func primes(c chan int) {
	for i := 0; ; i++ {
		// Implemented in primes_sieve.go.
		c <- GetPrime(i)
	}
}

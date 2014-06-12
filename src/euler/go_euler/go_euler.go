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

func Nth(c chan int, i int) int {
	for ; i > 1; i-- {
		<-c
	}
	return <-c
}

func Primes() chan int {
	// 2, 3, 5, 7, 11, 13, 15...
	src := make(chan int)
	out := make(chan int)
	go source(src)
	go filter(src, out, 2)
	return out
}

func source(c chan int) {
	for i := 2; ; i++ {
		c <- i
	}
}

func filter(in chan int, out chan int, divisor int) {
	next := <-in
	out <- next
	filtered := make(chan int)
	go filter(filtered, out, next)
	for i := range in {
		if i%divisor != 0 {
			filtered <- i
		}
	}
}

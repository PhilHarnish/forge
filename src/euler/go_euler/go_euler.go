package go_euler

import (
	"fmt"
	"github.com/onsi/ginkgo"
	"math"
	"sort"
	"sync"
)

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

func ChannelLength(c chan int) int {
	i := 0
	for _, ok := <-c; ok; _, ok = <-c {
		i++
	}
	return i
}

func Collect(c chan int) []int {
	result := []int{}
	for i := range c {
		result = append(result, i)
	}
	return result
}

func Debug(args ...interface{}) {
	fmt.Fprintln(ginkgo.GinkgoWriter, args...)
}

func Divisors(n int) chan int {
	c := make(chan int)
	go divisors(n, c)
	return c
}

func divisors(n int, out chan int) {
	factors := Collect(Factor(n))
	if len(factors) == 0 {
		out <- 1
		close(out)
		return
	}
	products := make(chan int, 2<<uint(len(factors)))
	divisorPowerSet(factors, 0, 1, products)
	close(products)
	c := Collect(products)
	sort.Ints(c)
	last := 0
	for _, i := range c {
		if last != i {
			last = i
			out <- i
		}
	}
	close(out)
}

func divisorPowerSet(factors []int, index int, product int, out chan int) {
	without := product
	with := product * factors[index]
	index++
	if index < len(factors) {
		divisorPowerSet(factors, index, without, out)
		divisorPowerSet(factors, index, with, out)
	} else {
		out <- without
		out <- with
	}
}

func Factor(n int) chan int {
	c := make(chan int)
	go factor(n, c)
	return c
}

func factor(n int, c chan int) {
	ceil := int(math.Sqrt(float64(n)))
	for i := range Primes() {
		for n%i == 0 {
			n /= i
			c <- i
		}
		if i > ceil {
			break
		}
	}
	if n > 1 {
		c <- n
	}
	close(c)
}

func Factorial(n int) int {
	result := n
	for n > 1 {
		n--
		result *= n
	}
	return result
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

// See: http://blog.golang.org/pipelines.
func Merge(in ...chan int) chan int {
	var wg sync.WaitGroup
	wg.Add(len(in))
	out := make(chan int)

	// Start an output goroutine for each input channel in in. output
	// copies values from c to out until c is closed, then calls wg.Done.
	output := func(c chan int) {
		for n := range c {
			out <- n
		}
		wg.Done()
	}
	for _, c := range in {
		go output(c)
	}

	// Start a goroutine to close out once all the output goroutines are
	// done. This must start after the wg.Add call.
	go func() {
		wg.Wait()
		close(out)
	}()
	return out
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

func Range(start, end int, args ...int) chan int {
	c := make(chan int)
	increment := 1
	if len(args) == 1 {
		increment = args[0]
	}
	go rangeSend(c, start, end, increment)
	return c
}

func rangeSend(c chan int, start, end, increment int) {
	for ; start < end; start += increment {
		c <- start
	}
	close(c)
}

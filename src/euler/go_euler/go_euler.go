package go_euler

import (
	"fmt"
	"github.com/onsi/ginkgo"
	"math"
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

var knownPrimes []int = []int{2, 3}
//var primesRwLock sync.RWMutex
//var generateLock sync.Mutex

func Primes() chan int {
	// 2, 3, 5, 7, 11, 13, 15...
	c := make(chan int)
	go primes(c)
	return c
}

func primes(c chan int) {
	for i := 0; ; i++ {
		if i >= len(knownPrimes) {
			GeneratePrime(i)
		}
		c <- knownPrimes[i]
	}
}

func GeneratePrime(ceil int) {
	generatePrime(ceil)
	// primesSieve(ceil) is available in primes_sieve.go.
}

func generatePrime(next int) {
	//generateLock.Lock()
	//defer generateLock.Unlock()
	// Generate the next prime starting where we left off.
	lastPrimeIndex := len(knownPrimes)
	test := knownPrimes[lastPrimeIndex-1]
	for i := lastPrimeIndex; i <= next; {
		test += 2
		if IsPrime(test) {
			//primesRwLock.Lock()
			knownPrimes = append(knownPrimes, test)
			i++
			//primesRwLock.Unlock()
		}
	}
}

func IsPrime(n int) bool {
	//primesRwLock.RLock()
	//defer primesRwLock.RUnlock()
	end := int(math.Sqrt(float64(n)))
	for i := 0; i < len(knownPrimes); i++ {
		prime := knownPrimes[i]
		if n%prime == 0 {
			return false
		} else if prime > end {
			return true
		}
	}
	// TODO(philharnish): Generate needed primes.
	panic(fmt.Sprintf("Unable to check primality for %d", n))
}

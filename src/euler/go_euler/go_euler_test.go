package go_euler_test

import (
	. "github.com/philharnish/forge/src/euler/go_euler"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

var _ = Describe("GoEuler",
	func() {
		Describe("ChainMultiply",
			func() {
				It("it doesn't output for empty channel",
					func() {
						c := make(chan int)
						close(c)
						products := ChainMultiply(c, 4)
						_, ok := <-products
						Expect(ok).To(Equal(false))
					})

				It("it returns products as they arrive",
					func() {
						p := ChainMultiply(Range(1, 5), 4)
						Expect([]int{<-p, <-p, <-p, <-p}).To(Equal([]int{1, 2, 6, 24}))
					})

				It("it handles zeros without errors",
					func() {
						p := ChainMultiply(Range(-2, 3), 4)
						Expect([]int{<-p, <-p}).To(Equal([]int{-2, 2}))
						// 0 in input has undocumented output so throw it away.
						<-p
						Expect([]int{<-p, <-p}).To(Equal([]int{1, 2}))
					})
			})

		Describe("ChannelLength",
			func() {
				It("counts 0 items in an empty channel",
					func() {
						c := make(chan int)
						close(c)
						Expect(ChannelLength(c)).To(Equal(0))
					})

				It("counts multiple items in a channel",
					func() {
						c := Range(0, 5)
						Expect(ChannelLength(c)).To(Equal(5))
					})
			})

		Describe("Collect",
			func() {
				It("collects empty channels",
					func() {
						s := make(chan int)
						close(s)
						c := Collect(s)
						Expect(len(c)).To(Equal(0))
						Expect(c).To(Equal([]int{}))
					})

				It("collects from channels",
					func() {
						c := Collect(Range(0, 5))
						Expect(len(c)).To(Equal(5))
						Expect(c).To(Equal([]int{0, 1, 2, 3, 4}))
					})
			})

		Describe("Divisors",
			func() {
				It("returns 1 divisor for '1'",
					func() {
						d := Divisors(1)
						Expect(<-d).To(Equal(1))
						_, ok := <-d
						Expect(ok).To(Equal(false))
					})

				It("returns 2 divisors for primes",
					func() {
						d := Divisors(13)
						Expect(<-d).To(Equal(1))
						Expect(<-d).To(Equal(13))
						_, ok := <-d
						Expect(ok).To(Equal(false))
					})

				It("handles many divisors",
					func() {
						d := Divisors(12)
						Expect(Collect(d)).To(Equal(
							[]int{1, 2, 3, 4, 6, 12}))
					})
			})

		Describe("Factor",
			func() {
				It("factors prime numbers",
					func() {
						f := Factor(3)
						Expect(Collect(f)).To(Equal([]int{3}))
					})

				It("factors composite numbers",
					func() {
						f := Factor(10)
						Expect(Collect(f)).To(Equal([]int{2, 5}))
					})

				It("factors numbers with duplicate composites",
					func() {
						f := Factor(16)
						Expect(Collect(f)).To(Equal([]int{2, 2, 2, 2}))
					})
			})

		Describe("Factorial",
			func() {
				It("returns small results",
					func() {
						Expect(Factorial(4)).To(Equal(4 * 3 * 2))
					})

				It("returns large results",
					func() {
						Expect(Factorial(10)).To(Equal(3628800))
					})
			})

		Describe("Fibonacci",
			func() {
				It("exports Fibonacci correctly",
					func() {
						Expect(Fibonacci).NotTo(BeNil())
					})

				It("returns expected values",
					func() {
						f := Fibonacci()
						Expect([]int{<-f, <-f, <-f, <-f}).To(Equal([]int{1, 2, 3, 5}))
					})
			})

		Describe("Merge",
			func() {
				It("merges int channels",
					func() {
						a := Range(0, 5)
						b := Range(0, 5)
						c := Merge(a, b)
						Expect(ChannelLength(c)).To(Equal(10))
					})
			})

		Describe("Nth",
			func() {
				It("exports Nth correctly",
					func() {
						Expect(Nth).NotTo(BeNil())
					})

				It("returns the Nth item in a channel",
					func() {
						c := Fibonacci()
						Expect(Nth(c, 4)).To(Equal(5))
					})
			})

		Describe("Primes",
			func() {
				It("exports Primes correctly",
					func() {
						Expect(Primes).NotTo(BeNil())
					})

				It("returns small primes",
					func() {
						f := Primes()
						Expect([]int{<-f, <-f, <-f, <-f}).To(Equal([]int{2, 3, 5, 7}))
					})

				It("returns larger primes",
					func() {
						f := Primes()
						Expect(Nth(f, 6)).To(Equal(13))
						Expect([]int{<-f, <-f, <-f, <-f}).To(Equal([]int{17, 19, 23, 29}))
					})
			})
	})

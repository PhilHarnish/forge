package go_euler_test

import (
	. "euler/go_euler"

	. "github.com/onsi/ginkgo"
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
						_, ok := <- products
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
						<- p
						Expect([]int{<-p, <-p}).To(Equal([]int{1, 2}))
					})
			})

		Describe("ChannelLength",
			func() {
				It("counts 0 items in an empty channel",
					func(work Done) {
						c := make(chan int)
						close(c)
						Expect(ChannelLength(c)).To(Equal(0))
						close(work)
					})

				It("counts multiple items in a channel",
					func(work Done) {
						c := Range(0, 5)
						Expect(ChannelLength(c)).To(Equal(5))
						close(work)
					})
			})

		Describe("Factor",
			func() {
				It("factors prime numbers",
					func() {
						f := Factor(3)
						Expect(<-f).To(Equal(3))
						Eventually(f).Should(BeClosed())
					})

				It("factors composite numbers",
					func() {
						f := Factor(10)
						Expect([]int{<-f, <-f}).To(Equal([]int{2, 5}))
						Eventually(f).Should(BeClosed())
					})

				It("factors numbers with duplicate composites",
					func() {
						f := Factor(16)
						Expect([]int{<-f, <-f, <-f, <-f}).To(Equal([]int{2, 2, 2, 2}))
						Eventually(f).Should(BeClosed())
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
					})
			})
	})

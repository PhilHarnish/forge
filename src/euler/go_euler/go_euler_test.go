package go_euler_test

import (
	. "euler/go_euler"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("GoEuler",
	func() {
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
	})

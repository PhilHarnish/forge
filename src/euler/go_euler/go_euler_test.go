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
						Expect(f()).To(Equal(3))
						Expect(f()).To(Equal(0))
					})
				It("factors composite numbers",
					func() {
						f := Factor(10)
						Expect(f()).To(Equal(2))
						Expect(f()).To(Equal(5))
						Expect(f()).To(Equal(0))
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
						Expect(f()).To(Equal(1))
						Expect(f()).To(Equal(2))
						Expect(f()).To(Equal(3))
						Expect(f()).To(Equal(5))
					})
			})
	})

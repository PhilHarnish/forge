package go_euler_test

import (
	. "euler/go_euler"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("GoEuler",
	func() {
		Describe("Fibonacci", func() {
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

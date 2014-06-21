package go_euler_test

import (
	. "euler/go_euler"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Problem12",
	func() {
		It("should handle given example",
			func() {
				Expect(Problem12(5)).To(Equal(28))
			})

		It("should handle problem asked",
			func() {
				Expect(Problem12(500)).To(Equal(76576500))
			})
	})

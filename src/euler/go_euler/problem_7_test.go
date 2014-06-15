package go_euler_test

import (
	. "euler/go_euler"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Problem7",
	func() {
		It("should handle given example",
			func() {
				Expect(Problem7(6)).To(Equal(13))
			})

		It("should handle problem asked",
			func() {
				Expect(Problem7(10001)).To(Equal(104743))
			})
	})

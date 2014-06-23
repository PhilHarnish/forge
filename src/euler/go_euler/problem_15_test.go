package go_euler_test

import (
	. "euler/go_euler"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Problem15",
	func() {
		It("should handle given example",
			func() {
				Expect(Problem15(2)).To(Equal(6))
			})

		It("should handle problem asked",
			func() {
				Expect(Problem15(20)).To(Equal(137846528820))
			})
	})

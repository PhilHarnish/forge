package go_euler_test

import (
	. "euler/go_euler"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Problem5",
	func() {
		It("should handle given example",
			func() {
				// Factoring [2, 10] and taking max for each gives:
				// 2*2*2 (from 8) * 3*3 (from 9) * 5 * 7 = 2520.
				Expect(Problem5(10)).To(Equal(2520))
			})

		It("should handle problem asked",
			func() {
				Expect(Problem5(20)).To(Equal(232792560))
			})
	})

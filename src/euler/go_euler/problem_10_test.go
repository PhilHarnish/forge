package go_euler_test

import (
	. "euler/go_euler"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Problem10",
	func() {
		It("should handle given example",
			func() {
				Expect(Problem10(10)).To(Equal(17))
			})

		It("should handle problem asked",
			func() {
				//Expect(Problem10(2000000)).To(Equal(142913828922))
				Expect(Problem10(500000)).To(Equal(9914236195))
				Expect(Problem10(500000)).To(Equal(9914236195))
			})
	})

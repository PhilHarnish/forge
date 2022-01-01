package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
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

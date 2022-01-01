package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
)

var _ = Describe("Problem10",
	func() {
		It("should handle given example",
			func() {
				Expect(Problem10(10)).To(Equal(17))
			})

		It("should handle problem asked",
			func() {
				Expect(Problem10(2000000)).To(Equal(142913828922))
			})
	})

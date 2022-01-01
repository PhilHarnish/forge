package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
)

var _ = Describe("Problem6",
	func() {
		It("should handle given example",
			func() {
				Expect(Problem6(10)).To(Equal(2640))
			})

		It("should handle problem asked",
			func() {
				Expect(Problem6(100)).To(Equal(25164150))
			})
	})

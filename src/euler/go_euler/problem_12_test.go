package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
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

package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
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

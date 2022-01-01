package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
)

var _ = Describe("Problem4",
	func() {
		It("should handle 1 digit products",
			func() {
				// 9 = 3 × 3
				Expect(Problem4(1)).To(Equal(9))
			})

		It("should handle 2 digit products",
			func() {
				// 9009 = 91 × 99.
				Expect(Problem4(2)).To(Equal(9009))
			})

		It("should handle 3 digit products",
			func() {
				Expect(Problem4(3)).To(Equal(906609))
			})
	})

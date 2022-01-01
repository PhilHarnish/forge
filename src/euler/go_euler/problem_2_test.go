package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
)

var _ = Describe("Problem2",
	func() {
		It("should handle small inputs",
			func() {
				// 1, 2, 3, 5, 8
				//    2 +      8 = 10
				Expect(Problem2(10)).To(Equal(10))
			})

		It("should solve problem",
			func() {
				Expect(Problem2(4000000)).To(Equal(4613732))
			})
	})

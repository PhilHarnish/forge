package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
)

var _ = Describe("Problem7",
	func() {
		It("should handle problem asked",
			func() {
				Expect(Problem9(1000)).To(Equal(31875000))
			})
	})

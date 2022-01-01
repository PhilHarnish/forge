package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
)

var _ = Describe("Problem3",
	func() {
		It("should handle small inputs",
			func() {
				Expect(Problem3(10)).To(Equal(5))
			})

		It("should handle large primes",
			func() {
				Expect(Problem3(97)).To(Equal(97))
			})

		It("should handle squares",
			func() {
				Expect(Problem3(49)).To(Equal(7))
			})
	})

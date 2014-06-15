package go_euler_test

import (
	. "euler/go_euler"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Problem7",
	func() {
		It("should handle problem asked",
			func() {
				Expect(Problem9(1000)).To(Equal(31875000))
			})
	})

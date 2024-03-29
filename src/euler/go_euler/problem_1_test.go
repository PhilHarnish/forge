package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/philharnish/forge/src/euler/go_euler"
)

var _ = Describe("Problem1",
	func() {
		It("exports correctly",
			func() {
				Expect(Problem1).NotTo(BeNil())
			})

		It("accepts variable args",
			func() {
				Expect(Problem1(0)).To(Equal(0))
				Expect(Problem1(2, 1)).To(Equal(1))
			})

		It("returns example value",
			func() {
				Expect(Problem1(10, 3, 5)).To(Equal(23))
			})

		It("returns requested value",
			func() {
				Expect(Problem1(1000, 3, 5)).To(Equal(233168))
			})
	})

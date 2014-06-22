package go_euler_test

import (
	. "euler/go_euler"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Problem14",
	func() {
		It("should handle given example",
			func() {
				// 9: len([9 28 14 7 22 11 34 17 52 26 13 40 20 10 5 16 8 4 2]) = 20
				Expect(Problem14(14)).To(Equal(9))
			})

		It("should handle problem asked",
			func() {
				Expect(Problem14(1000000)).To(Equal(837799))
			})

		XMeasure("with backfill, all",
			func(b Benchmarker) {
				b.Time("runtime",
					func() {
						output := Problem14(1000000)
						Expect(output).To(Equal(837799))
					})
			}, 50)
	})

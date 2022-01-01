package go_euler_test

import (
	"time"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	. "github.com/onsi/gomega/gmeasure"
	. "github.com/philharnish/forge/src/euler/go_euler"
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

		It("with backfill, all",
			func() {
				var experiment = NewExperiment("Problem14 benchmark")
				AddReportEntry(experiment.Name, experiment)
				experiment.Sample(
					func(idx int) {
						output := Problem14(1000000)
						Expect(output).To(Equal(837799))
					}, SamplingConfig{N: 100, Duration: time.Minute, NumParallel: 8})
			})
	})

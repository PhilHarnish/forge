package weight_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("CumulativeWeight", func() {
	It("returns 0 for nil", func() {
		Expect(weight.CumulativeWeight(nil)).To(Equal(0.0))
	})

	It("returns 0 for empty set", func() {
		Expect(weight.CumulativeWeight([]*weight.WeightedString{})).To(Equal(0.0))
	})

	It("returns weight for for 1 item", func() {
		Expect(weight.CumulativeWeight([]*weight.WeightedString{
			{
				Weight: .5,
			},
		})).To(Equal(0.5))
	})

	It("returns multiplication for 2+ items", func() {
		Expect(weight.CumulativeWeight([]*weight.WeightedString{
			{
				Weight: .5,
			},
			{
				Weight: .5,
			},
		})).To(Equal(0.25))
	})

	It("ignores nil items", func() {
		Expect(weight.CumulativeWeight([]*weight.WeightedString{
			nil,
			{
				Weight: .5,
			},
		})).To(Equal(0.5))
	})
})

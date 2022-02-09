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

var _ = Describe("WeightedStrings::String", func() {
	It("begins empty", func() {
		ws := weight.WeightedStrings{}
		Expect(ws.String()).To(Equal("0.00\t∅"))
	})

	It("formats 1 string", func() {
		ws := weight.WeightedStrings{Strings: []string{"example"}}
		Expect(ws.String()).To(Equal("0.00\texample"))
	})

	It("formats multiple strings", func() {
		ws := weight.WeightedStrings{Strings: []string{"a", "b", "c"}}
		Expect(ws.String()).To(Equal("0.00\ta\tb\tc"))
	})
})

var _ = Describe("CumulativeWeight", func() {
	It("returns 0 for nil", func() {
		Expect(weight.CumulativeWeight(nil)).To(Equal(0.0))
	})

	It("returns 0 for empty set", func() {
		Expect(weight.CumulativeWeight([]weight.WeightedString{})).To(Equal(0.0))
	})

	It("returns weight for for 1 item", func() {
		Expect(weight.CumulativeWeight([]weight.WeightedString{
			{
				Weight: .5,
			},
		})).To(Equal(0.5))
	})

	It("returns multiplication for 2+ items", func() {
		Expect(weight.CumulativeWeight([]weight.WeightedString{
			{
				Weight: .5,
			},
			{
				Weight: .5,
			},
		})).To(Equal(0.25))
	})
})

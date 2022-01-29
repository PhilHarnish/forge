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

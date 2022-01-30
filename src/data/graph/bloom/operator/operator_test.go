package operator_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/operator"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("And", func() {
	It("Implements String", func() {
		o := operator.And
		Expect(o.String([]string{"a", "b"})).To(Equal("AND(a, b)"))
	})
})

var _ = Describe("Or", func() {
	It("Implements String", func() {
		o := operator.Or
		Expect(o.String([]string{"a", "b"})).To(Equal("OR(a, b)"))
	})
})

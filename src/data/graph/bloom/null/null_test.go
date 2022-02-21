package null_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/null"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Node interfaces", func() {
	It("includes Root func", func() {
		Expect(null.Null.Root()).NotTo(BeNil())
	})

	It("includes Items func", func() {
		items := null.Null.Items(node.NodeAcceptAll)
		Expect(items).NotTo(BeNil())
		Expect(items.HasNext()).To(BeFalse())
		Expect(func() { items.Next() }).To(Panic())
	})

	It("includes String func", func() {
		Expect(null.Null.String()).To(Equal("Null: 0 ●"))
	})

	It("includes Root func", func() {
		Expect(null.Null.Root().String()).To(Equal("Node: 0 ●"))
	})
})

package span_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/span"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Node interfaces", func() {
	It("String", func() {
		Expect(span.NewSpan("test").String()).To(Equal("Span: 'test'->Node"))
	})

	It("Root without match", func() {
		Expect(span.NewSpan("test").Root().String()).To(Equal("Node: EST"))
	})

	It("Root with match", func() {
		Expect(span.NewSpan("test", node.NewNode(1)).Root().String()).To(Equal("Node: EST ◌◌◌◌●"))
	})

	It("Items", func() {
		s := span.NewSpan("test", node.NewNode(1))
		items := s.Items(node.NodeAcceptAll)
		Expect(items.HasNext()).To(BeTrue())
		path, next := items.Next()
		Expect(path).To(Equal("test"))
		Expect(next.String()).To(Equal("Node: 100 ●"))
	})

	It("StringChildren", func() {
		parent := span.NewSpan("test", node.NewNode(1))
		Expect(debug.StringChildren(parent)).To(matchers.LookLike(`
				Span: 'test'->Node: 100
				│◌◌◌◌●
				└test●->Node: 100
		`))
	})
})

package span_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/span"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Node interfaces", func() {
	It("String", func() {
		Expect(span.NewSpan("test").String()).To(Equal("Span('test', 0)"))
	})

	It("Root", func() {
		Expect(span.NewSpan("test").Root().String()).To(Equal("Node('EST', '    #', 0)"))
	})

	It("Items", func() {
		s := span.NewSpan("test")
		items := s.Items(node.NodeAcceptAll)
		Expect(items.HasNext()).To(BeTrue())
		path, next := items.Next()
		Expect(path).To(Equal("test"))
		Expect(next.String()).To(Equal("Null()"))
	})

	It("StringChildren", func() {
		Expect(node.StringChildren(span.NewSpan("test"))).To(matchers.LookLike(`
				Span('test', 0)
				└─test = Null()
		`))
	})
})

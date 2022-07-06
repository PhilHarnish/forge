package debug_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

var _ = Describe("TestGenerator", func() {
	It("implements NodeGenerator interface", func() {
		var generator node.NodeGenerator = debug.NewTestGenerator()
		Expect(generator).NotTo(BeNil())
	})

	It("returns items in given order", func() {
		expected := debug.TestItems{
			{String: "a", Weight: 1.0},
			{String: "b", Weight: 0.5},
			{String: "c", Weight: 0.0},
		}
		t := debug.NewTestIterator(node.NewNode(), &expected)
		generator := debug.NewTestGenerator()
		items := generator.Items(t)
		for _, expect := range expected {
			Expect(items.HasNext()).To(BeTrue())
			path, item := items.Next()
			Expect(path).To(Equal(expect.String))
			Expect(item.Root().MatchWeight).To(Equal(expect.Weight))
		}
	})
})

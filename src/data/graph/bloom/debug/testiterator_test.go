package debug_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

var _ = Describe("TestIterator", func() {
	It("is a no-op by default", func() {
		root := node.NewNode(1.0)
		t := debug.NewTestIterator(root, &debug.TestItems{})
		items := t.Items(node.NodeAcceptAll)
		Expect(t.Root()).To(Equal(root))
		Expect(items.HasNext()).To(BeFalse())
		Expect(func() { items.Next() }).To(Panic())
	})

	It("returns items in given order", func() {
		t := debug.NewTestIterator(node.NewNode(), &debug.TestItems{
			{String: "a", Weight: 1.0},
			{String: "b", Weight: 0.5},
			{String: "c", Weight: 0.0},
		})
		Expect(debug.StringChildren(t)).To(matchers.LookLike(`
			TestIterator
			├a●->TestIterator: 100
			├b●->TestIterator: 50
			└c ->TestIterator
		`))
	})
})

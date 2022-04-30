package order_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/null"
	"github.com/philharnish/forge/src/data/graph/bloom/order"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

var _ = Describe("Alphabetized", func() {
	It("is a no-op for null", func() {
		Expect(debug.StringChildren(order.Alphabetized(null.Null))).To(Equal("Null: 0"))
	})

	It("iterates children with equal weight in order", func() {
		t := trie.NewTrie()
		t.Add("a", 1)
		t.Add("z", .5)
		t.Add("b", 1)
		t.Add("y", .5)
		Expect(debug.StringChildren(order.Alphabetized(t))).To(matchers.LookLike(`
			Trie: abyz
			│◌●
			├a●->Trie: 100
			├b●->Trie: 100
			├y●->Trie: 50
			└z●->Trie: 50
		`))
	})

	It("preserves original order if there are ordering errors", func() {
		iterator := debug.NewTestIterator(node.NewNode(1.0), &debug.TestItems{
			{Weight: .50, String: "a"},
			{Weight: .75, String: "b"},
			{Weight: 1.0, String: "c"},
		})
		Expect(debug.StringChildren(order.Alphabetized(iterator))).To(matchers.LookLike(`
		  TestIterator: 100
			├a●->TestIterator: 50
			├b●->TestIterator: 75
			╪> Weights out of order: 0.75 > 0.5
			└c●->TestIterator: 100
			═> Weights out of order: 1 > 0.75
		`))
	})
})

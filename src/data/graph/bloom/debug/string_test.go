package debug_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

var _ = Describe("StringChildren", func() {
	It("Produces shallow string results", func() {
		t := trie.NewTrie(1)
		t.Add("a", 1.0)
		t.Add("b", 1.0)
		Expect(debug.StringChildren(t)).To(matchers.LookLike(`
			Trie: 100 ab
			│●●
			├a●->Trie: 100
			└b●->Trie: 100
		`))
	})

	It("Produces deeper string results", func() {
		child := trie.NewTrie(1)
		child.Add("a", 1.0)
		child.Add("b", 1.0)
		parent := trie.NewTrie()
		parent.Link("c", child)
		Expect(debug.StringChildren(parent, 2)).To(matchers.LookLike(`
			Trie: abC
			│◌●●
			└c●->Trie: 100 ab
			·│●●
			·├a●->Trie: 100
			·└b●->Trie: 100
		`))
	})

	It("Alerts when there are duplicate children", func() {
		iterator := debug.NewTestIterator(node.NewNode(), &debug.TestItems{
			{String: "a"}, {String: "b"}, {String: "b"}, {String: "a"},
		})
		Expect(debug.StringChildren(iterator)).To(matchers.LookLike(`
			TestIterator
			├a ->TestIterator
			├a ->TestIterator
			╪> Duplicate edge: Ⓐ
			├b ->TestIterator
			└b ->TestIterator
			═> Duplicate edge: Ⓑ
		`))
	})

	It("Alerts when children have illegal paths", func() {
		iterator := debug.NewTestIterator(node.NewNode(), &debug.TestItems{
			{String: "a"}, {String: "$"},
		})
		Expect(debug.StringChildren(iterator)).To(matchers.LookLike(`
			TestIterator
			├$ ->TestIterator
			╪> Invalid path: '$' not supported
			└a ->TestIterator
		`))
	})

	It("Alerts when children unsorted weights", func() {
		iterator := debug.NewTestIterator(node.NewNode(), &debug.TestItems{
			{String: "a", Weight: 0.0},
			{String: "b", Weight: 0.5},
			{String: "c", Weight: 1.0},
		})
		Expect(debug.StringChildren(iterator)).To(matchers.LookLike(`
			TestIterator
			├a ->TestIterator
			├b●->TestIterator: 50
			╪> Weights out of order: 0.5 > 0
			└c●->TestIterator: 100
			═> Weights out of order: 1 > 0.5
		`))
	})

	It("Follows specified path", func() {
		child := trie.NewTrie(1)
		parent := trie.NewTrie()
		parent.Link("a", child)
		parent.Link("b", child)
		child.Link("a", parent)
		child.Link("b", parent)
		Expect(debug.StringPath(parent, "abbab")).To(matchers.LookLike(`
			Trie: ab
			│◌●
			├a●->Trie: 100 ab
			││●◌●
			│├a ->Trie: ab
			││└2 children: ab
			│└b ->Trie: ab
			│ │◌●
			│ ├a●->Trie: 100 ab
			│ │└2 children: ab
			│ └b●->Trie: 100 ab
			│  │●◌●
			│  ├a ->Trie: ab
			│  ││◌●
			│  │├a●->Trie: 100 ab
			│  ││└2 children: ab
			│  │└b●->Trie: 100 ab
			│  │ └2 children: ab
			│  └b ->Trie: ab
			│   └2 children: ab
			└b●->Trie: 100 ab
			·└2 children: ab
		`))
	})
})

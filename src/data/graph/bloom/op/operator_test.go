package op_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

var _ = Describe("Process", func() {
	It("Does nothing for empty input", func() {
		operation := op.And()
		items := operation.Items(node.NodeAcceptAll)
		Expect(items.HasNext()).To(BeFalse())
	})

	Describe("And", func() {
		It("Returns all edges for 1 item", func() {
			t := extend(trie.NewTrie(1.0), "a")
			operation := op.And(t)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					AND(Trie('A', ' #', 0))
					a = Trie('', '#', 1)
			`))
		})

		It("Returns no edges for 2+ non-matching AND() operands", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "b")
			c := extend(trie.NewTrie(.1), "c")
			operation := op.And(c, a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					AND(Trie('C', ' #', 0), Trie('A', ' #', 0), Trie('B', ' #', 0))
			`))
		})
	})

	Describe("Or", func() {
		It("Returns all edges for 1 item", func() {
			t := extend(trie.NewTrie(1.0), "a")
			operation := op.Or(t)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					OR(Trie('A', ' #', 0))
					a = Trie('', '#', 1)
			`))
		})

		It("Returns matching OR() operands", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "b")
			c := extend(trie.NewTrie(.1), "c")
			operation := op.Or(c, a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
				OR(Trie('C', ' #', 0), Trie('A', ' #', 0), Trie('B', ' #', 0))
				a = Trie('', '#', 1)
				b = Trie('', '#', 0.5)
				c = Trie('', '#', 0.1)
			`))
		})
	})
})

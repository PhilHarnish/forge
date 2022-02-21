package op_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

var _ = Describe("process", func() {
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
					Trie('A', ' #', 0)
					└─a = Trie('', '#', 1)
			`))
		})

		It("Returns matching edges for 2+ items", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "a")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					AND(Trie('A', ' #', 0), Trie('A', ' #', 0))
					└─a = AND(Trie('', '#', 1), Trie('', '#', 0.5))
			`))
		})

		It("Recursively returns matches", func() {
			a := extend(trie.NewTrie(1.0), "a", "b")
			b := extend(trie.NewTrie(.5), "a", "b")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation, 2)).To(matchers.LookLike(`
					AND(Trie('AB', '  #', 0), Trie('AB', '  #', 0))
					└─a = AND(Trie('B', ' #', 0), Trie('B', ' #', 0))
					• └─b = AND(Trie('', '#', 1), Trie('', '#', 0.5))
			`))
		})

		It("Returns matches until discovering it is a dead end", func() {
			a := extend(trie.NewTrie(1.0), "a", "a", "b", "b")
			b := extend(trie.NewTrie(.5), "a", "a", "a", "b")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation, 2)).To(matchers.LookLike(`
					AND(Trie('AB', '    #', 0), Trie('AB', '    #', 0))
					└─a = AND(Trie('AB', '   #', 0), Trie('AB', '   #', 0))
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

		It("Abandons search immediately if a length match is impossible", func() {
			a := extend(trie.NewTrie(1.0), "a", "a")
			b := extend(trie.NewTrie(.5), "a")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					AND(Trie('A', '  #', 0), Trie('A', ' #', 0))
			`))
		})

		It("Abandons search immediately if a dependency is unsatisfiable", func() {
			a := extend(trie.NewTrie(1.0), "a", "b", "c")
			b := extend(trie.NewTrie(.5), "a", "a", "a")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					AND(Trie('ABC', '   #', 0), Trie('A', '   #', 0))
			`))
		})

		XIt("Supports shared multi-rune paths", func() {
			a := extend(trie.NewTrie(1.0), "a", "b", "c")
			b := extend(trie.NewTrie(.5), "abc")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					OR(Trie('A', ' #', 0), Trie('XYZ', '   #', 0))
					├─a = Trie('', '#', 1)
					└─xyz = Trie('', '#', 0.5)
			`))
		})

		It("Merges redundant OR(a, OR(b, c)) to OR(a, b, c)", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "b")
			c := extend(trie.NewTrie(.1), "c")
			operation := op.And(a, op.And(b, c))
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					AND(Trie('A', ' #', 0), Trie('B', ' #', 0), Trie('C', ' #', 0))
			`))
		})
	})

	Describe("Or", func() {
		It("Returns all edges for 1 item", func() {
			root := trie.NewTrie()
			root.Add("b", 0.5)
			root.Add("a", 1.0)
			operation := op.Or(root)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					Trie('ab', ' #', 0)
					├─a = Trie('', '#', 1)
					└─b = Trie('', '#', 0.5)
			`))
		})

		It("Returns all edges for 2+ item", func() {
			a := trie.NewTrie()
			a.Add("a", 1.0)
			b := trie.NewTrie()
			b.Add("b", 0.5)
			operation := op.Or(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					OR(Trie('A', ' #', 0), Trie('B', ' #', 0))
					├─a = Trie('', '#', 1)
					└─b = Trie('', '#', 0.5)
			`))
		})

		It("Carefully avoids duplicates", func() {
			a := trie.NewTrie()
			a.Add("a", 1.0)
			b := trie.NewTrie()
			b.Add("a", 0.5)
			operation := op.Or(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					OR(Trie('A', ' #', 0), Trie('A', ' #', 0))
					└─a = OR(Trie('', '#', 1), Trie('', '#', 0.5))
			`))
		})

		It("Returns matching OR() operands", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "b")
			c := extend(trie.NewTrie(.1), "c")
			operation := op.Or(c, a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					OR(Trie('C', ' #', 0), Trie('A', ' #', 0), Trie('B', ' #', 0))
					├─a = Trie('', '#', 1)
					├─b = Trie('', '#', 0.5)
					└─c = Trie('', '#', 0.1)
			`))
		})

		It("Supports (unique) multi-rune paths", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "xyz")
			operation := op.Or(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					OR(Trie('A', ' #', 0), Trie('XYZ', '   #', 0))
					├─a = Trie('', '#', 1)
					└─xyz = Trie('', '#', 0.5)
			`))
		})

		XIt("Supports duplicative multi-rune paths", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "abc")
			operation := op.Or(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					OR(Trie('C', ' #', 0), Trie('A', ' #', 0), Trie('B', ' #', 0))
					├─a = Trie('', '#', 1)
					├─b = Trie('', '#', 0.5)
					└─c = Trie('', '#', 0.1)
			`))
		})

		It("Merges redundant OR(a, OR(b, c)) to OR(a, b, c)", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "b")
			c := extend(trie.NewTrie(.1), "c")
			operation := op.Or(a, op.Or(b, c))
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					OR(Trie('A', ' #', 0), Trie('B', ' #', 0), Trie('C', ' #', 0))
					├─a = Trie('', '#', 1)
					├─b = Trie('', '#', 0.5)
					└─c = Trie('', '#', 0.1)
			`))
		})
	})

	Describe("Concat", func() {
		It("Returns all edges for 2+ item", func() {
			a := trie.NewTrie()
			a.Add("a", 1.0)
			b := trie.NewTrie()
			b.Add("b", 0.5)
			operation := op.Concat(a, b)
			Expect(node.StringChildren(operation, 3)).To(matchers.LookLike(`
					CONCAT(Trie('A', ' #', 0), Trie('B', ' #', 0))
					└─a = Trie('B', ' #', 0)
					• └─b = Trie('', '#', 0.5)
			`))
		})

		It("Traverses multiple paths if needed", func() {
			a := trie.NewTrie()
			a.Add("a", 1.0)
			a.Add("aa", .5)
			b := trie.NewTrie()
			b.Add("b", 0.5)
			operation := op.Concat(a, b)
			Expect(node.StringChildren(operation, 3)).To(matchers.LookLike(`
					CONCAT(Trie('A', ' ##', 0), Trie('B', ' #', 0))
					└─a = OR(CONCAT(Trie('A', '##', 1), Trie('B', ' #', 0)), Trie('B', ' #', 0))
					• ├─a = Trie('B', ' #', 0)
					• │ └─b = Trie('', '#', 0.5)
					• └─b = Trie('', '#', 0.5)
			`))
		})

		It("Merges redundant Concat calls", func() {
			a := trie.NewTrie()
			a.Add("a", 1.0)
			b := trie.NewTrie()
			b.Add("b", 0.5)
			c := trie.NewTrie()
			c.Add("c", 0.5)
			operation := op.Concat(a, op.Concat(b, c))
			Expect(node.StringChildren(operation, 3)).To(matchers.LookLike(`
					CONCAT(Trie('A', ' #', 0), Trie('B', ' #', 0), Trie('C', ' #', 0))
					└─a = CONCAT(Trie('B', ' #', 0), Trie('C', ' #', 0))
					• └─b = Trie('C', ' #', 0)
					• • └─c = Trie('', '#', 0.5)
			`))
		})
	})

	Describe("Join", func() {
		It("Returns all edges for 2+ item", func() {
			a := trie.NewTrie()
			a.Add("a", 1.0)
			b := trie.NewTrie()
			b.Add("b", 0.5)
			operation := op.Join("z", a, b)
			Expect(node.StringChildren(operation, 3)).To(matchers.LookLike(`
					CONCAT(Trie('A', ' #', 0), Span('z', 0), Trie('B', ' #', 0))
					└─a = CONCAT(Span('z', 0), Trie('B', ' #', 0))
					• └─z = Trie('B', ' #', 0)
					• • └─b = Trie('', '#', 0.5)
			`))
		})
	})
})

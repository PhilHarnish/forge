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
					Trie: A
					│◌●
					└a●->Trie: 100
			`))
		})

		It("Returns matching edges for 2+ items", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "a")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: A) && (Trie: A)): A
					│◌●
					└a●->((Trie: 100) && (Trie: 50)): 50
			`))
		})

		It("Recursively returns matches", func() {
			a := extend(trie.NewTrie(1.0), "a", "b")
			b := extend(trie.NewTrie(.5), "a", "b")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation, 2)).To(matchers.LookLike(`
					((Trie: AB) && (Trie: AB)): AB
					│◌◌●
					└a ->((Trie: B) && (Trie: B)): B
					·│◌●
					·└b●->((Trie: 100) && (Trie: 50)): 50
			`))
		})

		It("Returns matches until discovering it is a dead end", func() {
			a := extend(trie.NewTrie(1.0), "a", "a", "b", "b")
			b := extend(trie.NewTrie(.5), "a", "a", "a", "b")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation, 2)).To(matchers.LookLike(`
					((Trie: AB) && (Trie: AB)): AB
					│◌◌◌◌●
					└a ->((Trie: AB) && (Trie: AB)): AB
					·│◌◌◌●
			`))
		})

		It("Returns no edges for 2+ non-matching AND() operands", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "b")
			c := extend(trie.NewTrie(.1), "c")
			operation := op.And(c, a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: C) && (Trie: A) && (Trie: B)): ⒶⒷⒸ
			`))
		})

		It("Abandons search immediately if a length match is impossible", func() {
			a := extend(trie.NewTrie(1.0), "a", "a")
			b := extend(trie.NewTrie(.5), "a")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: A) && (Trie: A)): A
			`))
		})

		It("Abandons search immediately if a dependency is unsatisfiable", func() {
			a := extend(trie.NewTrie(1.0), "a", "b", "c")
			b := extend(trie.NewTrie(.5), "a", "a", "a")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: ABC) && (Trie: A)): AⒷⒸ
			`))
		})

		It("Supports shared multi-rune paths", func() {
			a := extend(trie.NewTrie(1.0), "a", "b", "c")
			b := extend(trie.NewTrie(.5), "abc")
			operation := op.And(a, b)
			Expect(node.StringChildren(operation, 3)).To(matchers.LookLike(`
					((Trie: ABC) && (Trie: ABC)): ABC
					│◌◌◌●
					└a ->((Trie: BC) && (((Span: 'bc' 0) + (Trie: 50)): BC)): BC
					·│◌◌●
					·└b ->((Trie: C) && (((Span: 'c' 0) + (Trie: 50)): C)): C
					· │◌●
					· └c●->((Trie: 100) && (Trie: 50)): 50
			`))
		})

		It("Merges redundant AND(a, AND(b, c)) to AND(a, b, c)", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "b")
			c := extend(trie.NewTrie(.1), "c")
			operation := op.And(a, op.And(b, c))
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: A) && (Trie: B) && (Trie: C)): ⒶⒷⒸ
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
					Trie: ab
					│◌●
					├a●->Trie: 100
					└b●->Trie: 50
			`))
		})

		It("Returns all edges for 2+ item", func() {
			a := trie.NewTrie()
			a.Add("a", 1.0)
			b := trie.NewTrie()
			b.Add("b", 0.5)
			operation := op.Or(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: A) || (Trie: B)): ab
					│◌●
					├a●->Trie: 100
					└b●->Trie: 50
			`))
		})

		It("Carefully avoids duplicates", func() {
			a := trie.NewTrie()
			a.Add("a", 1.0)
			b := trie.NewTrie()
			b.Add("a", 0.5)
			operation := op.Or(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: A) || (Trie: A)): A
					│◌●
					└a●->((Trie: 100) || (Trie: 50)): 100
			`))
		})

		It("Returns matching OR() operands", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "b")
			c := extend(trie.NewTrie(.1), "c")
			operation := op.Or(c, a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: C) || (Trie: A) || (Trie: B)): abc
					│◌●
					├a●->Trie: 100
					├b●->Trie: 50
					└c●->Trie: 10
			`))
		})

		It("Prefers the highest value result", func() {
			a := extend(trie.NewTrie(1.0), "ab")
			b := extend(trie.NewTrie(.5), "ab")
			c := extend(trie.NewTrie(.1), "ab")
			operation := op.Or(c, a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: AB) || (Trie: AB) || (Trie: AB)): AB
					│◌◌●
					└ab●->((Trie: 10) || (Trie: 100) || (Trie: 50)): 100
			`))
		})

		It("Supports (unique) multi-rune paths", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "xyz")
			operation := op.Or(a, b)
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: A) || (Trie: XYZ)): axyz
					│◌●◌●
					├a●->Trie: 100
					└xyz●->Trie: 50
			`))
		})

		It("Supports duplicative multi-rune paths", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "abc")
			operation := op.Or(a, b)
			Expect(node.StringChildren(operation, 3)).To(matchers.LookLike(`
					((Trie: A) || (Trie: ABC)): Abc
					│◌●◌●
					└a●->((Trie: 100) || (((Span: 'bc' 0) + (Trie: 50)): BC)): 100 BC
					·│●◌●
					·└bc●->Trie: 50
			`))
		})

		It("Reacts to paths that need to be split retroactively", func() {
			a := extend(trie.NewTrie(1.0), "abc")
			b := extend(trie.NewTrie(.5), "abc")
			c := extend(trie.NewTrie(.25), "a", "b", "c")
			operation := op.Or(a, b, c)
			Expect(node.StringChildren(operation, 5)).To(matchers.LookLike(`
					((Trie: ABC) || (Trie: ABC) || (Trie: ABC)): ABC
					│◌◌◌●
					└a ->((((Span: 'bc' 0) + (Trie: 100)): BC) || (((Span: 'bc' 0) + (Trie: 50)): BC) || (Trie: BC)): BC
					·│◌◌●
					·└b ->((((Span: 'c' 0) + (Trie: 100)): C) || (((Span: 'c' 0) + (Trie: 50)): C) || (Trie: C)): C
					· │◌●
					· └c●->((Trie: 100) || (Trie: 50) || (Trie: 25)): 100
			`))
		})

		It("Merges redundant OR(a, OR(b, c)) to OR(a, b, c)", func() {
			a := extend(trie.NewTrie(1.0), "a")
			b := extend(trie.NewTrie(.5), "b")
			c := extend(trie.NewTrie(.1), "c")
			operation := op.Or(a, op.Or(b, c))
			Expect(node.StringChildren(operation)).To(matchers.LookLike(`
					((Trie: A) || (Trie: B) || (Trie: C)): abc
					│◌●
					├a●->Trie: 100
					├b●->Trie: 50
					└c●->Trie: 10
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
					((Trie: A) + (Trie: B)): A
					│◌●
					└a ->Trie: B
					·│◌●
					·└b●->Trie: 50
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
					((Trie: A) + (Trie: B)): A
					│◌●●
					└a●->((((Trie: 100 A) + (Trie: B)): 100 A) || (Trie: B)): 100 ab
					·│●●
					·├a ->Trie: B
					·││◌●
					·│└b●->Trie: 50
					·└b●->Trie: 50
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
					((Trie: A) + (Trie: B) + (Trie: C)): A
					│◌●
					└a ->((Trie: B) + (Trie: C)): B
					·│◌●
					·└b ->Trie: C
					· │◌●
					· └c●->Trie: 50
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
					((Trie: A) + (Span: 'z' 0) + (Trie: B)): A
					│◌●
					└a ->((Span: 'z' 0) + (Trie: B)): Z
					·│◌●
					·└z ->Trie: B
					· │◌●
					· └b●->Trie: 50
			`))
		})
	})
})

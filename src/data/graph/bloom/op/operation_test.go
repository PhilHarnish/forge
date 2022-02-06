package op_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

var _ = Describe("Operations", func() {
	var a *trie.Trie
	var b *trie.Trie
	var vowels *trie.Trie
	var fruit *trie.Trie

	BeforeEach(func() {
		a = trie.NewTrie()
		b = trie.NewTrie()
		vowels = trie.NewTrie()
		for _, c := range "aeiou" {
			vowels.Link(string(c), trie.NewTrie(1.0))
		}
		apple := extend(trie.NewTrie(1.0), "pple")
		banana := extend(trie.NewTrie(1.0), "anana")
		fruit = trie.NewTrie()
		fruit.Link("a", apple)
		fruit.Link("b", banana)
	})

	Describe("And", func() {
		It("Returns Null for zero operands", func() {
			a := op.And()
			Expect(a.String()).To(Equal("Null()"))
		})

		It("Returns original for 1 operands", func() {
			original := trie.NewTrie(1.0)
			a := op.And(original)
			Expect(a.String()).To(Equal(original.String()))
		})

		It("Creates operation for 2+ operands", func() {
			o := op.And(a, b)
			Expect(o.String()).To(Equal("AND(Trie('', '', 0), Trie('', '', 0))"))
		})

		It("Returns empty result for empty nodes", func() {
			o := op.And(a, b)
			Expect(node.StringChildren(o)).To(matchers.LookLike(`
					AND(Trie('', '', 0), Trie('', '', 0))
			`))
		})
	})

	Describe("Or", func() {
		It("Returns Null for zero operands", func() {
			a := op.Or()
			Expect(a.String()).To(Equal("Null()"))
		})

		It("Returns original for 1 operands", func() {
			original := trie.NewTrie(1.0)
			a := op.Or(original)
			Expect(a.String()).To(Equal(original.String()))
		})

		It("Creates operation for 2+ operands", func() {
			o := op.Or(a, b)
			Expect(o.String()).To(Equal("OR(Trie('', '', 0), Trie('', '', 0))"))
		})
	})

	Describe("Concat", func() {
		It("Returns Null for zero operands", func() {
			a := op.Concat()
			Expect(a.String()).To(Equal("Null()"))
		})

		It("Returns original for 1 operands", func() {
			original := trie.NewTrie(1.0)
			a := op.Concat(original)
			Expect(a.String()).To(Equal(original.String()))
		})

		It("Creates operation for 2+ operands", func() {
			o := op.Concat(a, b)
			Expect(o.String()).To(Equal("CONCAT(Trie('', '', 0), Trie('', '', 0))"))
		})
	})

	Describe("Join", func() {
		It("Returns Null for zero operands", func() {
			a := op.Join("")
			Expect(a.String()).To(Equal("Null()"))
		})

		It("Returns original for 1 operands", func() {
			original := trie.NewTrie(1.0)
			a := op.Join("", original)
			Expect(a.String()).To(Equal(original.String()))
		})

		It("Creates operation for 2+ operands", func() {
			o := op.Join(" ", a, b)
			Expect(o.String()).To(Equal("CONCAT(Trie('', '', 0), Span(' ', 0), Trie('', '', 0))"))
		})

		It("Reuses Concat when separator is ''", func() {
			o := op.Join("", a, b)
			Expect(o.String()).To(Equal("CONCAT(Trie('', '', 0), Trie('', '', 0))"))
		})
	})
})

package op_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Operations", func() {
	var a *trie.Trie
	var b *trie.Trie

	BeforeEach(func() {
		a = trie.NewTrie()
		b = trie.NewTrie()
	})

	Describe("And", func() {
		It("Creates operation", func() {
			o := op.And(a, b)
			Expect(o.String()).To(Equal("(Trie('', '', 0) && Trie('', '', 0))"))
		})
	})

	Describe("Or", func() {
		It("Creates operation", func() {
			o := op.Or(a, b)
			Expect(o.String()).To(Equal("(Trie('', '', 0) || Trie('', '', 0))"))
		})
	})

	Describe("Concat", func() {
		It("Creates operation", func() {
			o := op.Concat(a, b)
			Expect(o.String()).To(Equal("(Trie('', '', 0) + Trie('', '', 0))"))
		})
	})

	Describe("Join", func() {
		It("Creates operation", func() {
			o := op.Join(' ', a, b)
			Expect(o.String()).To(Equal("JOIN(' ', Trie('', '', 0), Trie('', '', 0))"))
		})
	})
})

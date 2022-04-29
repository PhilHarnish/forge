package order_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
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
})

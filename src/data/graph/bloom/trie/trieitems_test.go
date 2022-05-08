package trie_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

func extend(item *trie.Trie, paths ...string) node.NodeIterator {
	for i := len(paths) - 1; i >= 0; i-- {
		parent := trie.NewTrie()
		err := parent.Link(paths[i], item)
		Expect(err).ShouldNot(HaveOccurred())
		item = parent
	}
	return item
}

func expectNext(s node.NodeItems, p string, w weight.Weight) node.NodeIterator {
	path, item := s.Next()
	Expect(path).To(Equal(p))
	if len(p) > 0 {
		Expect(item).NotTo(BeNil())
		Expect(item.Root().MatchWeight).To(Equal(w))
	} else {
		Expect(item).To(BeNil())
	}
	return item
}

var _ = Describe("Items", func() {
	It("Initially has no items", func() {
		t := trie.NewTrie()
		items := node.NodeAcceptAll.Items(t)
		Expect(items.HasNext()).To(BeFalse())
	})

	It("Iterates immediate children, best to worst", func() {
		t := trie.NewTrie()
		t.Link("c", trie.NewTrie(0.5))
		t.Link("a", trie.NewTrie(1.0))
		t.Link("b", trie.NewTrie(0.9))
		items := node.NodeAcceptAll.Items(t)
		expectNext(items, "a", 1.0)
		expectNext(items, "b", 0.9)
		expectNext(items, "c", 0.5)
		Expect(items.HasNext()).To(BeFalse())
	})

	It("Iterates deeply", func() {
		t := extend(trie.NewTrie(1.0), "a", "b", "c")
		t = expectNext(node.NodeAcceptAll.Items(t), "a", 0.0)
		t = expectNext(node.NodeAcceptAll.Items(t), "b", 0.0)
		t = expectNext(node.NodeAcceptAll.Items(t), "c", 1.0)
		Expect(node.NodeAcceptAll.Items(t).HasNext()).To(BeFalse())
	})
})

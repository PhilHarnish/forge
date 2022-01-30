package trie_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

func TestIteratorItems(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

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
		items := t.Items(node.NodeAcceptAll)
		expectNext(items, "", 0)
	})

	It("Returns nothing if no nodes are accepted", func() {
		t := trie.NewTrie()
		t.Link("a", trie.NewTrie(1.0))
		items := t.Items(node.NodeAcceptNone)
		expectNext(items, "", 0.0)
	})

	It("Iterates immediate children, best to worst", func() {
		t := trie.NewTrie()
		t.Link("c", trie.NewTrie(0.5))
		t.Link("a", trie.NewTrie(1.0))
		t.Link("b", trie.NewTrie(0.9))
		items := t.Items(node.NodeAcceptAll)
		expectNext(items, "a", 1.0)
		expectNext(items, "b", 0.9)
		expectNext(items, "c", 0.5)
		expectNext(items, "", 0.0)
	})

	It("Iterates deeply", func() {
		t := extend(trie.NewTrie(1.0), "a", "b", "c")
		t = expectNext(t.Items(node.NodeAcceptAll), "a", 0.0)
		t = expectNext(t.Items(node.NodeAcceptAll), "b", 0.0)
		t = expectNext(t.Items(node.NodeAcceptAll), "c", 1.0)
		expectNext(t.Items(node.NodeAcceptAll), "", 0.0)
	})
})

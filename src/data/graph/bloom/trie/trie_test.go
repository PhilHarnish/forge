package trie_test

import (
	"fmt"
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

func TestNode(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Link", func() {
	var root *trie.Trie

	BeforeEach(func() {
		root = trie.NewTrie()
	})

	It("Linked child is indicated in output", func() {
		err := root.Link("c", trie.NewTrie(1.0))
		Expect(err).ShouldNot(HaveOccurred())
		Expect(root.String()).To(Equal("Trie: C ◌●"))
	})

	It("Rejects empty links", func() {
		err := root.Link("", trie.NewTrie(1.0))
		Expect(err).Should(HaveOccurred())
	})

	It("Rejects illegal links", func() {
		err := root.Link("🚫", trie.NewTrie(1.0))
		Expect(err).Should(MatchError(
			"error while linking: '🚫' not supported"))
	})

	It("Rejects duplicate links", func() {
		err := root.Link("c", trie.NewTrie(1.0))
		Expect(err).ShouldNot(HaveOccurred())
		err = root.Link("c", trie.NewTrie(1.0))
		Expect(err).Should(MatchError("link 'c' already exists"))
	})

	It("Accepts multi-rune links", func() {
		err := root.Link("abc", trie.NewTrie(1.0))
		Expect(err).ShouldNot(HaveOccurred())
		Expect(root.String()).To(Equal("Trie: ABC ◌◌◌●"))
	})

	It("Multiple links eliminate requirement for parent", func() {
		for _, c := range "abc" {
			err := root.Link(string(c), trie.NewTrie(1.0))
			Expect(err).ShouldNot(HaveOccurred())
		}
		Expect(root.String()).To(Equal("Trie: abc ◌●"))
	})

	It("Requirements are inherited", func() {
		cursor := trie.NewTrie(1.0)
		for _, c := range []string{
			"a=Trie: A ◌●",
			"b=Trie: AB ◌◌●",
			"c=Trie: ABC ◌◌◌●",
			"a=Trie: ABC ◌◌◌◌●",
		} {
			next := trie.NewTrie()
			err := next.Link(string(c[0]), cursor)
			cursor = next
			Expect(err).ShouldNot(HaveOccurred())
			Expect(fmt.Sprintf("%c=%s", c[0], cursor)).To(Equal(c))
		}
	})
})

var _ = Describe("Get", func() {
	var root *trie.Trie

	BeforeEach(func() {
		root = trie.NewTrie()
		root.Link("a", trie.NewTrie(1.0))
	})

	It("Finds requested child", func() {
		child := root.Get("a")
		Expect(child.String()).To(Equal("Trie: 100 ●"))
	})

	It("Finds requested child recursively", func() {
		ancestor := trie.NewTrie()
		ancestor.Link("b", root)
		child := ancestor.Get("b").Get("a")
		Expect(child.String()).To(Equal("Trie: 100 ●"))
	})

	It("Returns nil, not error, for missing child", func() {
		child := root.Get("z")
		Expect(child).To(BeNil())
	})
})

var _ = Describe("Add", func() {
	var root *trie.Trie

	BeforeEach(func() {
		root = trie.NewTrie()
	})

	It("Adds a child to a new path", func() {
		err := root.Add("a", 1.0)
		Expect(err).NotTo(HaveOccurred())
		Expect(debug.StringChildren(root)).To(matchers.LookLike(`
				Trie: A
				│◌●
				└a●->Trie: 100
		`))
	})

	It("Extends an existing path", func() {
		root.Add("a", 1.0)
		err := root.Add("ab", 0.5)
		Expect(err).NotTo(HaveOccurred())
		Expect(debug.StringChildren(root, 2)).To(matchers.LookLike(`
				Trie: Ab
				│◌●●
				└a●->Trie: 100 B
				·│●●
				·└b●->Trie: 50
		`))
	})
})

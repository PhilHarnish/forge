package trie_test

import (
	"fmt"
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

func TestNode(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Match", func() {
	It("Initially does not match", func() {
		node := trie.NewTrie()
		Expect(node.String()).To(Equal("Trie('', '', 0)"))
	})

	It("Match indicated in String output", func() {
		node := trie.NewTrie()
		node.Match(0.5)
		Expect(node.String()).To(Equal("Trie('', '#', 0.5)"))
	})

	It("Rejects duplicate attempts", func() {
		node := trie.NewTrie()
		node.Match(0.5)
		Expect(func() {
			node.Match(0.5)
		}).To(Panic())
	})
})

var _ = Describe("Link", func() {
	var root *trie.Trie

	BeforeEach(func() {
		root = trie.NewTrie()
	})

	It("Linked child is indicated in output", func() {
		err := root.Link("c", trie.NewTrie(1.0))
		Expect(err).ShouldNot(HaveOccurred())
		Expect(root.String()).To(Equal("Trie('C', ' #', 0)"))
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
		Expect(root.String()).To(Equal("Trie('ABC', '   #', 0)"))
	})

	It("Multiple links eliminate requirement for parent", func() {
		for _, c := range "abc" {
			err := root.Link(string(c), trie.NewTrie(1.0))
			Expect(err).ShouldNot(HaveOccurred())
		}
		Expect(root.String()).To(Equal("Trie('abc', ' #', 0)"))
	})

	It("Requirements are inherited", func() {
		cursor := trie.NewTrie(1.0)
		for _, c := range []string{
			"a=Trie('A', ' #', 0)",
			"b=Trie('AB', '  #', 0)",
			"c=Trie('ABC', '   #', 0)",
			"a=Trie('ABC', '    #', 0)",
		} {
			next := trie.NewTrie()
			err := next.Link(string(c[0]), cursor)
			cursor = next
			Expect(err).ShouldNot(HaveOccurred())
			Expect(fmt.Sprintf("%c=%s", c[0], cursor)).To(Equal(c))
		}
	})
})

var _ = Describe("Satisfies", func() {
	It("Empty nodes do not satisfy by default (no exits)",
		func() {
			node := trie.NewTrie(1.0)
			Expect(node.Satisfies(node)).To(BeFalse())
		})

	It("Fully populated node satisfies anything", func() {
		populated := trie.NewTrie()
		for _, c := range mask.ALPHABET {
			populated.Link(string(c), trie.NewTrie(1.0))
		}
		for _, c := range mask.ALPHABET {
			seeker := trie.NewTrie()
			seeker.Link(string(c), trie.NewTrie(1.0))
			Expect(populated.Satisfies(seeker)).To(BeTrue())
		}
	})
})

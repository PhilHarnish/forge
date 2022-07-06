package op_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

func TestOp(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Test")
}

func extend(item *trie.Trie, paths ...string) *trie.Trie {
	for i := len(paths) - 1; i >= 0; i-- {
		parent := trie.NewTrie()
		err := parent.Link(paths[i], item)
		Expect(err).ShouldNot(HaveOccurred())
		item = parent
	}
	return item
}

var _ = Describe("Root", func() {
	It("is initially empty", func() {
		a := trie.NewTrie()
		o := op.And(a, a)
		Expect(o.Root().String()).To(Equal("Node"))
	})

	It("includes weights", func() {
		a := trie.NewTrie(1.0)
		o := op.And(a, a)
		Expect(o.Root().String()).To(Equal("Node: 100 ●"))
	})

	It("includes required characters", func() {
		a := trie.NewTrie()
		a.MaskPath("abc")
		o := op.And(a, a)
		Expect(o.Root().String()).To(Equal("Node: ABC ◌◌◌●"))
	})
})

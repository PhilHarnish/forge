package cursor_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/cursor"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

func TestCursor(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Cursor tests")
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

var _ = Describe("Cursor.NewCursor", func() {
	It("Initially empty", func() {
		cursor := cursor.NewCursor(nil)
		Expect(cursor.String()).To(Equal("Cursor('', <nil>)"))
	})

	It("Accepts a Trie", func() {
		root := extend(trie.NewTrie(1.0), "a", "b", "c")
		cursor := cursor.NewCursor(root)
		Expect(cursor.String()).To(Equal("Cursor('', Trie('ABC', '   #', 0))"))
	})
})

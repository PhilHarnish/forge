package op_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
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

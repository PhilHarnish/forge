package retrie_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("ReTrie", func() {
	It("is initially empty", func() {
		trie := retrie.NewReTrie("", 1.0)
		Expect(node.StringChildren(trie, 2)).To(matchers.LookLike(`
			ReTrie('', '#', 1)
		`))
	})

	It("matches specified character", func() {
		trie := retrie.NewReTrie("x", 1.0)
		Expect(node.StringChildren(trie)).To(matchers.LookLike(`
			ReTrie('X', ' #', 0)
			└─x = ReTrie('', '#', 1)
		`))
	})
})

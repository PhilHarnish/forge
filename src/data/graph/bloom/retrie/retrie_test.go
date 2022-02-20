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

	It("matches specified characters", func() {
		trie := retrie.NewReTrie("abc", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie('ABC', '   #', 0)
				└─abc = ReTrie('', '#', 1)
		`))
	})

	It("matches simple character class", func() {
		trie := retrie.NewReTrie("[abc]", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie('abc', ' #', 0)
				├─a = ReTrie('', '#', 1)
				├─b = ReTrie('', '#', 1)
				└─c = ReTrie('', '#', 1)
		`))
	})

	It("matches sandwiched character classes", func() {
		trie := retrie.NewReTrie("a[bc]d", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie('AbcD', '   #', 0)
				└─a = ReTrie('bcD', '  #', 0)
				• ├─b = ReTrie('D', ' #', 0)
				• │ └─d = ReTrie('', '#', 1)
				• └─c = ReTrie('D', ' #', 0)
				• • └─d = ReTrie('', '#', 1)
		`))
	})

	It("matches complex character classes", func() {
		trie := retrie.NewReTrie("[a-cxyz]", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie('abcxyz', ' #', 0)
				├─a = ReTrie('', '#', 1)
				├─b = ReTrie('', '#', 1)
				├─c = ReTrie('', '#', 1)
				├─x = ReTrie('', '#', 1)
				├─y = ReTrie('', '#', 1)
				└─z = ReTrie('', '#', 1)
		`))
	})

	It("matches simple repeats", func() {
		trie := retrie.NewReTrie("a{2}", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie('A', '  #', 0)
				└─a = ReTrie('A', ' #', 0)
				• └─a = ReTrie('', '#', 1)
		`))
	})
})

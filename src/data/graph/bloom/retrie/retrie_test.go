package retrie_test

import (
	"fmt"
	"strings"
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

func traverse(source node.NodeIterator, path ...string) string {
	acc := strings.Builder{}
	acc.WriteString(source.String() + "\n")
	for _, part := range path {
		child := find(source, part)
		if child == nil {
			acc.WriteString(fmt.Sprintf("%s = nil\n", part))
			break
		} else {
			acc.WriteString(fmt.Sprintf("%s = %s\n", part, child.String()))
		}
		source = child
	}
	return acc.String()
}

func find(source node.NodeIterator, path string) (result node.NodeIterator) {
	items := source.Items(node.NodeAcceptAll)
	for items.HasNext() {
		itemPath, item := items.Next()
		if path == itemPath {
			return item
		}
	}
	return result
}

var _ = Describe("ReTrie", func() {
	It("is initially empty", func() {
		trie := retrie.NewReTrie("", 1.0)
		Expect(node.StringChildren(trie, 2)).To(matchers.LookLike(`
				ReTrie: 100
		`))
	})

	It("rejects invalid input", func() {
		Expect(func() { retrie.NewReTrie("[(", 1.0) }).To(Panic())
	})
})

var _ = Describe("ReTrie Header + Metadata", func() {
	It("implements Header provider and Metadata provider", func() {
		trie := retrie.NewReTrie("a", 1.0)
		var headerProvider query.QueryHeaderProvider = trie
		var metadatProvider node.NodeMetadataProvider = trie
		Expect(headerProvider).NotTo(BeNil())
		Expect(metadatProvider).NotTo(BeNil())
	})

	It("initially has no special headers or metadata", func() {
		trie := retrie.NewReTrie("a", 1.0)
		Expect(trie.Header()).NotTo(BeNil())
		Expect(trie.Header().Labels()).To(HaveLen(0))
		Expect(trie.Metadata("a")).To(HaveLen(0))
	})

	It("has numbered headers for numbered capture groups", func() {
		trie := retrie.NewReTrie("(a)(b)(c)", 1.0)
		Expect(trie.Header().Labels()).To(Equal([]string{"1", "2", "3"}))
	})

	It("has named headers for named capture groups", func() {
		trie := retrie.NewReTrie("(?P<first>a)(?P<second>b)(?P<third>c)", 1.0)
		Expect(trie.Header().Labels()).To(Equal([]string{"first", "second", "third"}))
	})

	It("provides metadata on matches", func() {
		trie := retrie.NewReTrie("(a)(b)(c)", 1.0)
		metadata := trie.Metadata("abc")
		Expect(metadata).To(HaveLen(3))
		for i, expected := range []string{"a", "b", "c"} {
			Expect(metadata[i].Weight).To(Equal(1.0))
			Expect(metadata[i].String).To(Equal(expected))
		}
	})
})

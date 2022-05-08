package retrie_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

func traverse(source node.NodeIterator, path ...string) ([]string, []node.NodeItems) {
	acc := make([]node.NodeItems, 0, len(path)+1)
	for _, part := range path {
		items := node.NodeAcceptAll.Items(source)
		acc = append(acc, items)
		source = find(items, part)
		if source == nil {
			break
		}
	}
	if source != nil {
		acc = append(acc, node.NodeAcceptAll.Items(source))
	}
	return path, acc
}

func find(items node.NodeItems, path string) node.NodeIterator {
	for items.HasNext() {
		itemPath, item := items.Next()
		if path == itemPath {
			return item
		}
	}
	return nil
}

var _ = Describe("ReTrie", func() {
	It("is initially empty", func() {
		trie := retrie.NewReTrie("", 1.0)
		Expect(debug.StringChildren(trie, 2)).To(matchers.LookLike(`
				ReTrie: 100
		`))
	})

	It("rejects invalid input", func() {
		Expect(func() { retrie.NewReTrie("[(", 1.0) }).To(Panic())
	})
})

var _ = Describe("Special syntax", func() {
	BeforeEach(func() {
		retrie.ClearRegistry()
		child := retrie.NewReTrie("xyz", 1.0)
		retrie.Register("child", child)
	})

	AfterEach(func() {
		retrie.ClearRegistry()
	})

	It("matches {child} pattern", func() {
		trie := retrie.NewReTrie(`a{child}b`, 1.0)
		Expect(trie.Labels()).To(Equal([]string{"$child"}))
		Expect(debug.StringChildren(trie, 3)).To(matchers.LookLike(`
			ReTrie: ABXYZ
			│◌◌◌◌◌●
			└a ->((ReTrie: XYZ) + (ReTrie: B)): BXYZ
			·│◌◌◌◌●
			·└xyz ->ReTrie: B
			·   │◌●
			·   └b●->ReTrie: 100
		`))
	})

	It("fails to parse {child pattern", func() {
		Expect(func() {
			retrie.NewReTrie(`a{childb`, 1.0)
		}).To(Panic())
	})

	It("matches {child}{x,y} pattern", func() {
		trie := retrie.NewReTrie(`a{child}{1,2}b`, 1.0)
		Expect(debug.StringChildren(trie, 4)).To(matchers.LookLike(`
			ReTrie: ABXYZ
			│◌◌◌◌◌●◌◌●
			└a ->((ReTrie: XYZ) + (ReTrie: Bxyz)): BXYZ
			·│◌◌◌◌●◌◌●
			·└xyz ->ReTrie: Bxyz
			·   │◌●◌◌●
			·   ├b●->ReTrie: 100
			·   └xyz ->ReTrie: B
			·      │◌●
			·      └b●->ReTrie: 100
		`))
	})

	It("fails to parse {child.{x,y} pattern", func() {
		Expect(func() {
			retrie.NewReTrie(`a{child.{x,y}`, 1.0)
		}).To(Panic())
	})

	It("matches {child}+ repeats", func() {
		trie := retrie.NewReTrie("a{child}+", 1.0)
		Expect(debug.StringChildren(trie, 4)).To(matchers.LookLike(`
			ReTrie: AXYZ
			│◌◌◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌●···
			└a ->((ReTrie: XYZ) + (((ReTrie: XYZ) + <cycle>): XYZ)): XYZ
			·│◌◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●···
			·└xyz●->((ReTrie: XYZ) + <cycle>): XYZ
			·   │●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●···
			·   └xyz●->((ReTrie: XYZ) + <cycle>): XYZ
			·      │●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●···
			·      └xyz●->((ReTrie: XYZ) + <cycle>): XYZ
		`))
	})

	It("matches {child}+ repeats with suffix", func() {
		trie := retrie.NewReTrie("a{child}+b", 1.0)
		Expect(debug.StringChildren(trie, 4)).To(matchers.LookLike(`
			ReTrie: ABXYZ
			│◌◌◌◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●●···
			└a ->((ReTrie: XYZ) + (ReTrie: Bxyz)): BXYZ
			·│◌◌◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌●···
			·└xyz ->ReTrie: Bxyz
			·   │◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌●···
			·   ├b●->ReTrie: 100
			·   └xyz ->ReTrie: Bxyz
			·      │◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌●···
			·      ├b●->ReTrie: 100
			·      └xyz ->ReTrie: Bxyz
		`))
	})

	It("matches alternate children", func() {
		retrie.Register("a", retrie.NewReTrie("aab", 1.0))
		retrie.Register("b", retrie.NewReTrie("abb", 1.0))
		retrie.Register("c", retrie.NewReTrie("bbb", 1.0))
		trie := retrie.NewReTrie("({a}|{b}|{c}|aba)", 1.0)
		Expect(debug.StringChildren(trie, 4)).To(matchers.LookLike(`
			ReTrie: aB
			│◌◌◌●
			├a ->ReTrie: aB
			││◌◌●
			│├ab●->ReTrie: 100
			│└b ->ReTrie: ab
			│ │◌●
			│ ├a●->ReTrie: 100
			│ └b●->ReTrie: 100
			└bbb●->ReTrie: 100
		`))
	})

	It("merges duplicate expressions", func() {
		retrie.Register("a", retrie.NewReTrie("ab|aba|abaa", 1.0))
		retrie.Register("b", retrie.NewReTrie("ab|aba|abaa", 1.0))
		trie := retrie.NewReTrie("({a}|{b}|{b}|{a}|ab|aba|abaa)", 1.0)
		Expect(debug.StringChildren(trie, 4)).To(matchers.LookLike(`
			ReTrie: AB
			│◌◌●●●
			└a ->ReTrie: aB
			·│◌●●●
			·└b●->ReTrie: 100 A
			· │●●●
			· └a●->ReTrie: 100 A
			·  │●●
			·  └a●->((ReTrie: 100) || (ReTrie: 100) || (ReTrie: 100) || (ReTrie: 100)): 100
		`))
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
		paths, items := traverse(trie, "a")
		Expect(trie.Metadata(paths, items)).To(HaveLen(0))
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
		paths, items := traverse(trie, "a", "b", "c")
		metadata := trie.Metadata(paths, items)
		Expect(metadata).To(HaveLen(3))
		for i, expected := range []string{"a", "b", "c"} {
			Expect(metadata[i].Weight).To(Equal(1.0))
			Expect(metadata[i].String).To(Equal(expected))
		}
	})
})

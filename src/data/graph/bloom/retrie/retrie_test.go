package retrie_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
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
				ReTrie: 100
		`))
	})

	It("rejects invalid input", func() {
		Expect(func() { retrie.NewReTrie("[(", 1.0) }).To(Panic())
	})
})

var _ = Describe("ReTrie syntax", func() {
	It("matches specified character", func() {
		trie := retrie.NewReTrie("x", 1.0)
		Expect(node.StringChildren(trie)).To(matchers.LookLike(`
				ReTrie: X
				│◌●
				└x●->ReTrie: 100
		`))
	})

	It("ignores ^ and $", func() {
		trie := retrie.NewReTrie("^x$", 1.0)
		Expect(node.StringChildren(trie)).To(matchers.LookLike(`
				ReTrie: X
				│◌●
				└x●->ReTrie: 100
		`))
	})

	It("matches specified characters", func() {
		trie := retrie.NewReTrie("abc", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: ABC
				│◌◌◌●
				└abc●->ReTrie: 100
		`))
	})

	It("matches simple character class", func() {
		trie := retrie.NewReTrie("[abc]", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: abc
				│◌●
				├a●->ReTrie: 100
				├b●->ReTrie: 100
				└c●->ReTrie: 100
		`))
	})

	It("matches sandwiched character classes", func() {
		trie := retrie.NewReTrie("a[bc]d", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: AbcD
				│◌◌◌●
				└a ->ReTrie: bcD
				·│◌◌●
				·├b ->ReTrie: D
				·││◌●
				·│└d●->ReTrie: 100
				·└c ->ReTrie: D
				· │◌●
				· └d●->ReTrie: 100
		`))
	})

	It("matches complex character classes", func() {
		trie := retrie.NewReTrie("[a-cxyz]", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: abcxyz
				│◌●
				├a●->ReTrie: 100
				├b●->ReTrie: 100
				├c●->ReTrie: 100
				├x●->ReTrie: 100
				├y●->ReTrie: 100
				└z●->ReTrie: 100
		`))
	})

	It("matches \\w special character classes", func() {
		trie := retrie.NewReTrie(`\w`, 1.0)
		Expect(trie.String()).To(Equal("ReTrie: abcdefghijklmnopqrstuvwxyz ◌●"))
	})

	It("matches [:alpha:] character classes", func() {
		trie := retrie.NewReTrie(`[[:alpha:]]`, 1.0)
		Expect(trie.String()).To(Equal("ReTrie: abcdefghijklmnopqrstuvwxyz ◌●"))
	})

	It("matches dot", func() {
		trie := retrie.NewReTrie(".", 1.0)
		Expect(trie.String()).To(Equal("ReTrie: abcdefghijklmnopqrstuvwxyz -' ◌●"))
		items := trie.Items(node.NodeAcceptAll)
		seen := mask.Mask(0b0)
		for items.HasNext() {
			path, _ := items.Next()
			pathMask, _ := mask.EdgeMask(path)
			seen |= pathMask
		}
		Expect(mask.MaskString(seen, mask.NONE)).To(Equal(mask.ALPHABET))
	})

	It("matches dot and full range the same way", func() {
		dot := retrie.NewReTrie(".", 1.0)
		fullRange := retrie.NewReTrie("[a-z '-]", 1.0)
		Expect(dot.String()).To(Equal(fullRange.String()))
	})

	It("matches question mark", func() {
		trie := retrie.NewReTrie("ab?", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: Ab
				│◌●●
				└a●->ReTrie: 100 B
				·│●●
				·└b●->ReTrie: 100
		`))
	})

	It("matches question mark with suffix", func() {
		trie := retrie.NewReTrie("ab?c", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: AbC
				│◌◌●●
				└a ->ReTrie: bC
				·│◌●●
				·├b ->ReTrie: C
				·││◌●
				·│└c●->ReTrie: 100
				·└c●->ReTrie: 100
		`))
	})

	It("matches question mark with tricky suffix", func() {
		trie := retrie.NewReTrie("a(?:bxyz)?[a-c]", 1.0)
		Expect(node.StringChildren(trie, 6)).To(matchers.LookLike(`
				ReTrie: Abcxyz
				│◌◌●◌◌◌●
				└a ->ReTrie: abcxyz
				·│◌●◌◌◌●
				·├a●->ReTrie: 100
				·├b●->ReTrie: 100 abcXYZ
				·││●◌◌◌●
				·│└xyz ->ReTrie: abc
				·│   │◌●
				·│   ├a●->ReTrie: 100
				·│   ├b●->ReTrie: 100
				·│   └c●->ReTrie: 100
				·└c●->ReTrie: 100
		`))
	})

	It("matches simple repeats", func() {
		trie := retrie.NewReTrie("a{2}", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: A
				│◌◌●
				└a ->ReTrie: A
				·│◌●
				·└a●->ReTrie: 100
		`))
	})

	It("matches simple ranges", func() {
		trie := retrie.NewReTrie("a{2,4}", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: A
				│◌◌●●●
				└a ->ReTrie: A
				·│◌●●●
				·└a●->ReTrie: 100 A
				· │●●●
				· └a●->ReTrie: 100 A
				·  │●●
				·  └a●->ReTrie: 100
		`))
	})

	It("matches hidden middle alternatives", func() {
		trie := retrie.NewReTrie("abc|axc", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: AbCx
				│◌◌◌●
				└a ->ReTrie: bCx
				·│◌◌●
				·├bc●->ReTrie: 100
				·└xc●->ReTrie: 100
		`))
	})

	It("matches alternatives which cannot be easily simplified", func() {
		trie := retrie.NewReTrie("abc|acd|xyz", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: abcdxyz
				│◌◌◌●
				├a ->ReTrie: bCd
				││◌◌●
				│├bc●->ReTrie: 100
				│└cd●->ReTrie: 100
				└xyz●->ReTrie: 100
		`))
	})

	It("matches empty alternative", func() {
		trie := retrie.NewReTrie("abc|xyz|", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: 100 abcxyz
				│●◌◌●
				├abc●->ReTrie: 100
				└xyz●->ReTrie: 100
		`))
	})

	It("matches (?:non|capturing|groups|with|different|sizes)", func() {
		trie := retrie.NewReTrie("(?:a|bbbb|xyz)", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: abxyz
				│◌●◌●●
				├a●->ReTrie: 100
				├bbbb●->ReTrie: 100
				└xyz●->ReTrie: 100
		`))
	})

	It("matches (?:non|capturing|groups|with|shared|prefix)", func() {
		trie := retrie.NewReTrie("(?:aaabc|aabc|abc)", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: ABC
				│◌◌◌●●●
				└a ->ReTrie: aBC
				·│◌◌●●●
				·├a ->ReTrie: aBC
				·││◌◌●●
				·│├abc●->ReTrie: 100
				·│└bc●->ReTrie: 100
				·└bc●->ReTrie: 100
		`))
	})

	It("matches (?:non|capturing|groups|with|mixed|prefix)", func() {
		trie := retrie.NewReTrie("(?:aabc|abc|xyz)", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: abcxyz
				│◌◌◌●●
				├a ->ReTrie: aBC
				││◌◌●●
				│├abc●->ReTrie: 100
				│└bc●->ReTrie: 100
				└xyz●->ReTrie: 100
		`))
	})

	It("matches +", func() {
		trie := retrie.NewReTrie("a+", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: A
				│◌●●●···
				└a●->ReTrie: 100 A
				·│●●●···
				·└a●->ReTrie: 100 A
				· │●●●···
				· └a●->ReTrie: 100 A
		`))
	})

	It("matches + with suffix", func() {
		trie := retrie.NewReTrie("a+xyz", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: AXYZ
				│◌◌◌◌●●●···
				└a ->ReTrie: aXYZ
				·│◌◌◌●●●···
				·├xyz●->ReTrie: 100
				·└a ->ReTrie: aXYZ
				· │◌◌◌●●●···
				· ├xyz●->ReTrie: 100
				· └a ->ReTrie: aXYZ
		`))
	})

	It("matches [abc]+ with suffix", func() {
		trie := retrie.NewReTrie("[ab]+xyz", 1.0)
		Expect(node.StringChildren(trie, 2)).To(matchers.LookLike(`
				ReTrie: abXYZ
				│◌◌◌◌●●●···
				├a ->ReTrie: abXYZ
				││◌◌◌●●●···
				│├xyz●->ReTrie: 100
				│├a ->ReTrie: abXYZ
				│└b ->ReTrie: abXYZ
				└b ->ReTrie: abXYZ
				·│◌◌◌●●●···
				·├xyz●->ReTrie: 100
				·├a ->ReTrie: abXYZ
				·└b ->ReTrie: abXYZ
		`))
	})

	It("matches + with duplicate literal suffix", func() {
		trie := retrie.NewReTrie("a+a", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: A
				│◌◌●●●···
				└a ->ReTrie: A
				·│◌●●●···
				·└a●->ReTrie: 100 A
				· │●●●···
				· └a●->ReTrie: 100 A
				·  │●●●···
				·  └a●->ReTrie: 100 A
		`))
	})

	It("matches multiple +s", func() {
		trie := retrie.NewReTrie("a+b+", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: AB
				│◌◌●●●···
				└a ->ReTrie: aB
				·│◌●●●···
				·├b●->ReTrie: 100 B
				·││●●●···
				·│└b●->ReTrie: 100 B
				·│ │●●●···
				·│ └b●->ReTrie: 100 B
				·└a ->ReTrie: aB
				· │◌●●●···
				· ├b●->ReTrie: 100 B
				· ││●●●···
				· │└b●->ReTrie: 100 B
				· └a ->ReTrie: aB
				·  │◌●●●···
				·  ├b●->ReTrie: 100 B
				·  └a ->ReTrie: aB
		`))
	})

	It("matches + with duplicate range suffix", func() {
		trie := retrie.NewReTrie("a+[a-b]", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: Ab
				│◌◌●●●···
				└a ->ReTrie: ab
				·│◌●●●···
				·├a●->ReTrie: 100 ab
				·││●●●···
				·│├a●->ReTrie: 100 ab
				·│││●●●···
				·││├a●->ReTrie: 100 ab
				·││└b●->ReTrie: 100
				·│└b●->ReTrie: 100
				·└b●->ReTrie: 100
		`))
	})

	It("matches range+ with duplicate literal suffix", func() {
		trie := retrie.NewReTrie("[a-b]+a", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: Ab
				│◌◌●●●···
				├a ->ReTrie: Ab
				││◌●●●···
				│├a●->ReTrie: 100 Ab
				│││●●●···
				││├a●->ReTrie: 100 Ab
				││└b ->ReTrie: Ab
				│└b ->ReTrie: Ab
				│ │◌●●●···
				│ ├a●->ReTrie: 100 Ab
				│ └b ->ReTrie: Ab
				└b ->ReTrie: Ab
				·│◌●●●···
				·├a●->ReTrie: 100 Ab
				·││●●●···
				·│├a●->ReTrie: 100 Ab
				·│└b ->ReTrie: Ab
				·└b ->ReTrie: Ab
				· │◌●●●···
				· ├a●->ReTrie: 100 Ab
				· └b ->ReTrie: Ab
		`))
	})

	It("matches range+ with duplicate range suffix", func() {
		trie := retrie.NewReTrie("[a-b]+[a-b]", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: ab
				│◌◌●●●···
				├a ->ReTrie: ab
				││◌●●●···
				│├a●->ReTrie: 100 ab
				│││●●●···
				││├a●->ReTrie: 100 ab
				││└b●->ReTrie: 100 ab
				│└b●->ReTrie: 100 ab
				│ │●●●···
				│ ├a●->ReTrie: 100 ab
				│ └b●->ReTrie: 100 ab
				└b ->ReTrie: ab
				·│◌●●●···
				·├a●->ReTrie: 100 ab
				·││●●●···
				·│├a●->ReTrie: 100 ab
				·│└b●->ReTrie: 100 ab
				·└b●->ReTrie: 100 ab
				· │●●●···
				· ├a●->ReTrie: 100 ab
				· └b●->ReTrie: 100 ab
		`))
	})

	It("splits rune blocks as needed", func() {
		trie := retrie.NewReTrie("[a-bd-e]?[d-e]", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: abde
				│◌●●
				├a ->ReTrie: de
				││◌●
				│├d●->ReTrie: 100
				│└e●->ReTrie: 100
				├b ->ReTrie: de
				││◌●
				│├d●->ReTrie: 100
				│└e●->ReTrie: 100
				├d●->ReTrie: 100 de
				││●●
				│├d●->ReTrie: 100
				│└e●->ReTrie: 100
				└e●->ReTrie: 100 de
				·│●●
				·├d●->ReTrie: 100
				·└e●->ReTrie: 100
		`))
	})

	FIt("splits many rune blocks", func() {
		trie := retrie.NewReTrie("[ab]?[bc]?[cd]?", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: 100 abcd
				│●●●●
				├c●->ReTrie: 100
				││●●
				│├c●->ReTrie: 100
				│└d●->ReTrie: 100
				├d●->ReTrie: 100
				├a●->ReTrie: 100 bcd
				││●●●
				│├b●->ReTrie: 100 cd
				│││●●
				││├c●->ReTrie: 100
				││└d●->ReTrie: 100
				│└c●->ReTrie: 100 cd
				│ │●●
				│ ├c●->ReTrie: 100
				│ └d●->ReTrie: 100
				└b●->ReTrie: 100 bcd
				·│●●●
				·├b●->ReTrie: 100 cd
				·││●●
				·│├c●->ReTrie: 100
				·│└d●->ReTrie: 100
				·└c●->ReTrie: 100 cd
				· │●●
				· ├c●->ReTrie: 100
				· └d●->ReTrie: 100
		`))
	})

	It("matches .+ with suffix", func() {
		trie := retrie.NewReTrie(".+", 1.0)
		depth := 3
		var item node.NodeIterator = trie
		Expect(item.String()).To(Equal("ReTrie: abcdefghijklmnopqrstuvwxyz -' ◌●●●···"))
		for depth > 0 {
			depth--
			items := item.Items(node.NodeAcceptAll)
			Expect(items.HasNext()).To(BeTrue())
			_, item = items.Next()
			Expect(item.String()).To(Equal("ReTrie: 100 abcdefghijklmnopqrstuvwxyz -' ●●●···"))
			count := 1 // One extracted already.
			for items.HasNext() {
				items.Next()
				count++
			}
			Expect(count).To(Equal(mask.SIZE))
		}
	})

	It("matches alternative +s", func() {
		trie := retrie.NewReTrie("^(?:(?:a+)|(?:b+))$", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: ab
				│◌●●●···
				├a●->ReTrie: 100 A
				││●●●···
				│└a●->ReTrie: 100 A
				│ │●●●···
				│ └a●->ReTrie: 100 A
				└b●->ReTrie: 100 B
				·│●●●···
				·└b●->ReTrie: 100 B
				· │●●●···
				· └b●->ReTrie: 100 B
		`))
	})

	It("matches alternative +s with suffix", func() {
		trie := retrie.NewReTrie("^(?:(?:a+)|(?:b+))xy$", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: abXY
				│◌◌◌●●●···
				├a ->ReTrie: aXY
				││◌◌●●●···
				│├xy●->ReTrie: 100
				│└a ->ReTrie: aXY
				│ │◌◌●●●···
				│ ├xy●->ReTrie: 100
				│ └a ->ReTrie: aXY
				└b ->ReTrie: bXY
				·│◌◌●●●···
				·├xy●->ReTrie: 100
				·└b ->ReTrie: bXY
				· │◌◌●●●···
				· ├xy●->ReTrie: 100
				· └b ->ReTrie: bXY
		`))
	})

	It("matches (?:group|of|choices)+ with alt suffix", func() {
		trie := retrie.NewReTrie("(?:a|bbbbb)+(?:xxx|yyyyyy)", 1.0)
		Expect(node.StringChildren(trie, 2)).To(matchers.LookLike(`
				ReTrie: abxy
				│◌◌◌◌●●●···
				├a ->ReTrie: abxy
				││◌◌◌●●●···
				│├xxx●->ReTrie: 100
				│├yyyyyy●->ReTrie: 100
				│├a ->ReTrie: abxy
				│└bbbbb ->ReTrie: abxy
				└bbbbb ->ReTrie: abxy
				·    │◌◌◌●●●···
				·    ├xxx●->ReTrie: 100
				·    ├yyyyyy●->ReTrie: 100
				·    ├a ->ReTrie: abxy
				·    └bbbbb ->ReTrie: abxy
		`))
	})

	It("matches (?:group|of|choices)+ which require 3x len strings", func() {
		trie := retrie.NewReTrie("(?:aaa|bbb)+(?:xxx|yyy)", 1.0)
		Expect(node.StringChildren(trie, 2)).To(matchers.LookLike(`
				ReTrie: abxy
				│◌◌◌◌◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●···
				├aaa ->ReTrie: abxy
				│  │◌◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●···
				│  ├xxx●->ReTrie: 100
				│  ├yyy●->ReTrie: 100
				│  ├aaa ->ReTrie: abxy
				│  └bbb ->ReTrie: abxy
				└bbb ->ReTrie: abxy
				·  │◌◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●◌◌●···
				·  ├xxx●->ReTrie: 100
				·  ├yyy●->ReTrie: 100
				·  ├aaa ->ReTrie: abxy
				·  └bbb ->ReTrie: abxy
		`))
	})

	It("matches *", func() {
		trie := retrie.NewReTrie("ab*", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: Ab
				│◌●●●···
				└a●->ReTrie: 100 B
				·│●●●···
				·└b●->ReTrie: 100 B
				· │●●●···
				· └b●->ReTrie: 100 B
		`))
	})

	It("matches * with suffix", func() {
		trie := retrie.NewReTrie("ab*xyz", 1.0)
		Expect(node.StringChildren(trie, 4)).To(matchers.LookLike(`
				ReTrie: AbXYZ
				│◌◌◌◌●●●···
				└a ->ReTrie: bXYZ
				·│◌◌◌●●●···
				·├b ->ReTrie: bXYZ
				·││◌◌◌●●●···
				·│├xyz●->ReTrie: 100
				·│└b ->ReTrie: bXYZ
				·│ │◌◌◌●●●···
				·│ ├xyz●->ReTrie: 100
				·│ └b ->ReTrie: bXYZ
				·└xyz●->ReTrie: 100
		`))
	})

	It("matches multiple *s", func() {
		trie := retrie.NewReTrie("a*b*", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: 100 ab
				│●●●···
				├a●->ReTrie: 100 ab
				││●●●···
				│├b●->ReTrie: 100 B
				│││●●●···
				││└b●->ReTrie: 100 B
				│└a●->ReTrie: 100 ab
				│ │●●●···
				│ ├b●->ReTrie: 100 B
				│ └a●->ReTrie: 100 ab
				└b●->ReTrie: 100 B
				·│●●●···
				·└b●->ReTrie: 100 B
				· │●●●···
				· └b●->ReTrie: 100 B
		`))
	})

	It("matches alternative *s", func() {
		trie := retrie.NewReTrie("^(?:(?:a*)|(?:b*))$", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: 100 ab
				│●●●···
				├a●->ReTrie: 100 A
				││●●●···
				│└a●->ReTrie: 100 A
				│ │●●●···
				│ └a●->ReTrie: 100 A
				└b●->ReTrie: 100 B
				·│●●●···
				·└b●->ReTrie: 100 B
				· │●●●···
				· └b●->ReTrie: 100 B
		`))
	})

	It("matches alternative *s with suffix", func() {
		trie := retrie.NewReTrie("^(?:(?:a*)|(?:b*))xy$", 1.0)
		Expect(node.StringChildren(trie, 3)).To(matchers.LookLike(`
				ReTrie: abXY
				│◌◌●●●···
				├a ->ReTrie: aXY
				││◌◌●●●···
				│├xy●->ReTrie: 100
				│└a ->ReTrie: aXY
				│ │◌◌●●●···
				│ ├xy●->ReTrie: 100
				│ └a ->ReTrie: aXY
				├xy●->ReTrie: 100
				└b ->ReTrie: bXY
				·│◌◌●●●···
				·├xy●->ReTrie: 100
				·└b ->ReTrie: bXY
				· │◌◌●●●···
				· ├xy●->ReTrie: 100
				· └b ->ReTrie: bXY
		`))
	})

	It("matches capturing groups", func() {
		trie := retrie.NewReTrie("(a|b)(x|y)", 1.0)
		Expect(node.StringChildren(trie, 2)).To(matchers.LookLike(`
				ReTrie: abxy
				│◌◌●
				├a ->ReTrie: xy
				││◌●
				│├x●->ReTrie: 100
				│└y●->ReTrie: 100
				└b ->ReTrie: xy
				·│◌●
				·├x●->ReTrie: 100
				·└y●->ReTrie: 100
		`))
	})

	It("matches optional capturing groups", func() {
		trie := retrie.NewReTrie("(a|b)?(x|y)", 1.0)
		Expect(node.StringChildren(trie, 2)).To(matchers.LookLike(`
				ReTrie: abxy
				│◌●●
				├a ->ReTrie: xy
				││◌●
				│├x●->ReTrie: 100
				│└y●->ReTrie: 100
				├b ->ReTrie: xy
				││◌●
				│├x●->ReTrie: 100
				│└y●->ReTrie: 100
				├x●->ReTrie: 100
				└y●->ReTrie: 100
		`))
	})

	It("rejects \\b boundary", func() {
		Expect(func() { retrie.NewReTrie(`a\bb`, 1.0) }).To(Panic())
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

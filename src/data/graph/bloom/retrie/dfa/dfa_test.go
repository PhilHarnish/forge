package dfa_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie/dfa"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("nfaToDfa", func() {
	It("is initially empty", func() {
		result := dfa.Dfa("", 1.0)
		Expect(node.StringChildren(result, 2)).To(matchers.LookLike(`
				DFA{1,2}: 100
		`))
	})

	It("rejects invalid input", func() {
		Expect(func() { dfa.Dfa("[(", 1.0) }).To(Panic())
	})
})

var _ = Describe("Regexp syntax", func() {
	It("matches specified character", func() {
		n := dfa.Dfa("x", 1.0)
		Expect(node.StringChildren(n)).To(matchers.LookLike(`
				DFA{1}: X
				│◌●
				└x●->DFA{2}: 100
		`))
	})

	It("ignores ^ and $", func() {
		n := dfa.Dfa("^x$", 1.0)
		Expect(node.StringChildren(n)).To(matchers.LookLike(`
				DFA{1,2}: X
				│◌●
				└x●->DFA{3,4}: 100
		`))
	})

	It("matches specified characters", func() {
		n := dfa.Dfa("abc", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
				DFA{1}: ABC
				│◌◌◌●
				└abc●->DFA{4}: 100
		`))
	})

	It("matches simple character class", func() {
		n := dfa.Dfa("[abc]", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
				DFA{1}: abc
				│◌●
				├a●->DFA{2}: 100
				├b●->DFA{2}: 100
				└c●->DFA{2}: 100
		`))
	})

	It("matches sandwiched character classes", func() {
		n := dfa.Dfa("a[bc]d", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
				DFA{1}: AbcD
				│◌◌◌●
				└a ->DFA{2}: bcD
				·│◌◌●
				·├b ->DFA{3}: D
				·││◌●
				·│└d●->DFA{4}: 100
				·└c ->DFA{3}: D
				· │◌●
				· └d●->DFA{4}: 100
		`))
	})

	It("matches complex character classes", func() {
		n := dfa.Dfa("[a-cxyz]", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
				DFA{1}: abcxyz
				│◌●
				├a●->DFA{2}: 100
				├b●->DFA{2}: 100
				├c●->DFA{2}: 100
				├x●->DFA{2}: 100
				├y●->DFA{2}: 100
				└z●->DFA{2}: 100
		`))
	})

	It("matches \\w special character classes", func() {
		n := dfa.Dfa(`\w`, 1.0)
		Expect(n.String()).To(Equal("DFA{1}: abcdefghijklmnopqrstuvwxyz ◌●"))
	})

	It("matches [:alpha:] character classes", func() {
		n := dfa.Dfa(`[[:alpha:]]`, 1.0)
		Expect(n.String()).To(Equal("DFA{1}: abcdefghijklmnopqrstuvwxyz ◌●"))
	})

	It("matches dot", func() {
		n := dfa.Dfa(".", 1.0)
		Expect(n.String()).To(Equal("DFA{1}: abcdefghijklmnopqrstuvwxyz -' ◌●"))
		items := n.Items(node.NodeAcceptAll)
		seen := mask.Mask(0b0)
		for items.HasNext() {
			path, _ := items.Next()
			pathMask, _ := mask.EdgeMask(path)
			seen |= pathMask
		}
		Expect(mask.MaskString(seen, mask.NONE)).To(Equal(mask.ALPHABET))
	})

	It("matches dot and full range the same way", func() {
		dot := dfa.Dfa(".", 1.0)
		fullRange := dfa.Dfa("[a-z '-]", 1.0)
		Expect(dot.String()).To(Equal(fullRange.String()))
	})

	It("matches question mark", func() {
		n := dfa.Dfa("ab?", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
				DFA{1}: Ab
				│◌●●
				└a●->DFA{2,3,4}: 100 B
				·│●●
				·└b●->DFA{4}: 100
		`))
	})

	It("matches question mark with suffix", func() {
		n := dfa.Dfa("ab?c", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
				DFA{1}: AbC
				│◌◌●●
				└a ->DFA{2,3,4}: bC
				·│◌●●
				·├bc●->DFA{5}: 100
				·└c●->DFA{5}: 100
		`))
	})

	XIt("matches question mark with tricky suffix", func() {
		n := dfa.Dfa("a(?:bxyz)?[a-c]", 1.0)
		Expect(node.StringChildren(n, 4)).To(matchers.LookLike(`
				DFA{1}: ABcXYZ
				│◌◌●◌◌◌●
				└a ->DFA{2,6,7}: aBcXYZ
				·│◌●◌◌◌●
				·├bxyz ->DFA{7}: abc
				·│   │◌●
				·│   ├a●->DFA{8}: 100
				·│   ├b●->DFA{8}: 100
				·│   └c●->DFA{8}: 100
				·├a●->DFA{8}: 100
				·└c●->DFA{8}: 100
		`))
	})

	It("matches simple repeats", func() {
		n := dfa.Dfa("a{2}", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
				DFA{1}: A
				│◌◌●
				└aa●->DFA{3}: 100
		`))
	})

	It("matches simple ranges", func() {
		n := dfa.Dfa("a{2,4}", 1.0)
		Expect(node.StringChildren(n, 4)).To(matchers.LookLike(`
				DFA{1}: A
				│◌◌●●●
				└aa●->DFA{3,6,7}: 100 A
				· │●●●
				· └a●->DFA{4,5,7}: 100 A
				·  │●●
				·  └a●->DFA{7}: 100
		`))
	})

	It("matches hidden middle alternatives", func() {
		n := dfa.Dfa("abc|axc", 1.0)
		Expect(node.StringChildren(n, 4)).To(matchers.LookLike(`
				DFA{1}: AbCx
				│◌◌◌●
				└a ->DFA{2,4,6}: bCx
				·│◌◌●
				·├bc●->DFA{7}: 100
				·└xc●->DFA{7}: 100
		`))
	})

	It("matches alternatives which cannot be easily simplified", func() {
		n := dfa.Dfa("abc|acd|xyz", 1.0)
		Expect(node.StringChildren(n, 4)).To(matchers.LookLike(`
				DFA{1,7,10}: abcdxyz
				│◌◌◌●
				├a ->DFA{2,4,6}: bCd
				││◌◌●
				│├bc●->DFA{11}: 100
				│└cd●->DFA{11}: 100
				└xyz●->DFA{11}: 100
		`))
	})

	It("matches empty alternative", func() {
		n := dfa.Dfa("abc|xyz|", 1.0)
		Expect(node.StringChildren(n, 4)).To(matchers.LookLike(`
				DFA{1,4,7,8,9,10}: 100 abcxyz
				│●◌◌●
				├abc●->DFA{10}: 100
				└xyz●->DFA{10}: 100
		`))
	})

	It("matches (?:non|capturing|groups|with|different|sizes)", func() {
		n := dfa.Dfa("(?:a|bbbb|xyz)", 1.0)
		Expect(node.StringChildren(n, 4)).To(matchers.LookLike(`
				DFA{1,2,6,7,10}: abxyz
				│◌●◌●●
				├a●->DFA{11}: 100
				├bbbb●->DFA{11}: 100
				└xyz●->DFA{11}: 100
		`))
	})

	It("matches (?:non|capturing|groups|with|shared|prefix)", func() {
		n := dfa.Dfa("(?:aaabc|aabc|abc)", 1.0)
		Expect(node.StringChildren(n, 4)).To(matchers.LookLike(`
				DFA{1}: ABC
				│◌◌◌●●●
				└a ->DFA{2,9,11}: aBC
				·│◌◌●●●
				·├a ->DFA{3,6,8}: aBC
				·││◌◌●●
				·│├abc●->DFA{12}: 100
				·│└bc●->DFA{12}: 100
				·└bc●->DFA{12}: 100
		`))
	})

	It("matches (?:non|capturing|groups|with|mixed|prefix)", func() {
		n := dfa.Dfa("(?:aabc|abc|xyz)", 1.0)
		Expect(node.StringChildren(n, 4)).To(matchers.LookLike(`
				DFA{1,8,11}: abcxyz
				│◌◌◌●●
				├a ->DFA{2,5,7}: aBC
				││◌◌●●
				│├abc●->DFA{12}: 100
				│└bc●->DFA{12}: 100
				└xyz●->DFA{12}: 100
		`))
	})

	It("matches +", func() {
		n := dfa.Dfa("a+", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
				DFA{1}: A
				│◌●●●···
				└a●->DFA{1,2,3}: 100 A
				·│●●●···
				·└a●->DFA{1,2,3}: 100 A
				· │●●●···
				· └a●->DFA{1,2,3}: 100 A
		`))
	})

	XIt("dfa example online", func() {
		n := dfa.Dfa("(a|b)*ba", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
				TODO.
		`))
	})
})

var _ = Describe("GraphVizString", func() {
	It("is initially empty", func() {
		result := dfa.Dfa("", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				"1,2" [shape=doublecircle]
			}
		`))
	})

	It("branching paths", func() {
		result := dfa.Dfa("abc|acd|xyz", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				// 1,7,10 does not match
				"1,7,10" -> "2,4,6" [label="a"]
				// 2,4,6 does not match
				"2,4,6" -> "3" [label="b"]
				// 3 does not match
				"3" -> "11" [label="c"]
				"11" [shape=doublecircle]
				"2,4,6" -> "5" [label="c"]
				// 5 does not match
				"5" -> "11" [label="d"]
				"1,7,10" -> "8" [label="x"]
				// 8 does not match
				"8" -> "9" [label="y"]
				// 9 does not match
				"9" -> "11" [label="z"]
			}
		`))
	})

	It("looping paths", func() {
		result := dfa.Dfa("[ab]+", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				// 1 does not match
				"1" -> "1,2,3" [label="[ab]"]
				"1,2,3" [shape=doublecircle]
				"1,2,3" -> "1,2,3" [label="[ab]"]
			}
		`))
	})

	It("dfa example online", func() {
		result := dfa.Dfa("(a|b)*ba", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
		digraph G {
			// 1,2,4,5 does not match
			"1,2,4,5" -> "1,2,3,4,5" [label="[ab]"]
			// 1,2,3,4,5 does not match
			"1,2,3,4,5" -> "1,2,3,4,5" [label="[ab]"]
			"1,2,3,4,5" -> "6" [label="b"]
			// 6 does not match
			"6" -> "7" [label="a"]
			"7" [shape=doublecircle]
			"1,2,4,5" -> "6" [label="b"]
		}
		`))
	})
})

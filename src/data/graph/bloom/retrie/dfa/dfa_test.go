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

	It("matches question mark with tricky suffix", func() {
		n := dfa.Dfa("a(?:bxyz)?[a-c]", 1.0)
		Expect(node.StringChildren(n, 4)).To(matchers.LookLike(`
				DFA{1}: Abcxyz
				│◌◌●◌◌◌●
				└a ->DFA{2,6,7}: abcxyz
				·│◌●◌◌◌●
				·├a●->DFA{8}: 100
				·├b●->DFA{3,8}: 100 abcXYZ
				·││●◌◌◌●
				·│└xyz ->DFA{7}: abc
				·│   │◌●
				·│   ├a●->DFA{8}: 100
				·│   ├b●->DFA{8}: 100
				·│   └c●->DFA{8}: 100
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

	It("dfa example online", func() {
		n := dfa.Dfa("(a|b)*ab", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
			DFA{1,2,4,5}: Ab
			│◌◌●●●···
			├a ->DFA{1,2,3,4,5,6}: ab
			││◌●●●···
			│├a ->DFA{1,2,3,4,5,6}: ab
			│││◌●●●···
			││├a ->DFA{1,2,3,4,5,6}: ab
			││└b●->DFA{1,2,3,4,5,7}: 100 Ab
			│└b●->DFA{1,2,3,4,5,7}: 100 Ab
			│ │●◌●●●···
			│ ├a ->DFA{1,2,3,4,5,6}: ab
			│ └b ->DFA{1,2,3,4,5}: Ab
			└b ->DFA{1,2,3,4,5}: Ab
			·│◌◌●●●···
			·├a ->DFA{1,2,3,4,5,6}: ab
			·││◌●●●···
			·│├a ->DFA{1,2,3,4,5,6}: ab
			·│└b●->DFA{1,2,3,4,5,7}: 100 Ab
			·└b ->DFA{1,2,3,4,5}: Ab
			· │◌◌●●●···
			· ├a ->DFA{1,2,3,4,5,6}: ab
			· └b ->DFA{1,2,3,4,5}: Ab
		`))
	})

	It("dfa example online (variant)", func() {
		n := dfa.Dfa("(a|b)*ba", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
			DFA{1,2,4,5}: Ab
			│◌◌●●●···
			├a ->DFA{1,2,3,4,5}: Ab
			││◌◌●●●···
			│├a ->DFA{1,2,3,4,5}: Ab
			│││◌◌●●●···
			││├a ->DFA{1,2,3,4,5}: Ab
			││└b ->DFA{1,2,3,4,5,6}: Ab
			│└b ->DFA{1,2,3,4,5,6}: Ab
			│ │◌●●●···
			│ ├a●->DFA{1,2,3,4,5,7}: 100 ab
			│ └b ->DFA{1,2,3,4,5,6}: Ab
			└b ->DFA{1,2,3,4,5,6}: Ab
			·│◌●●●···
			·├a●->DFA{1,2,3,4,5,7}: 100 ab
			·││●◌●●●···
			·│├a ->DFA{1,2,3,4,5}: Ab
			·│└b ->DFA{1,2,3,4,5,6}: Ab
			·└b ->DFA{1,2,3,4,5,6}: Ab
			· │◌●●●···
			· ├a●->DFA{1,2,3,4,5,7}: 100 ab
			· └b ->DFA{1,2,3,4,5,6}: Ab
		`))
	})

	XIt("providers within a cycle", func() {
		n := dfa.Dfa("abc(wxc|wyzbc)*d", 1.0)
		Expect(node.StringChildren(n, 3)).To(matchers.LookLike(`
			DFA{1}: ABCDwxyz
			│◌◌◌◌●◌◌●◌●●◌●●●···
			└abc ->DFA{4,5,14,15}: bcdwxyz
			·  │◌●◌◌●◌●●◌●●●···
			·  ├w ->DFA{6,8,12}: bCdwxyz
			·  ││◌◌◌●◌●●◌●●●···
			·  │├xc ->DFA{4,5,13,14,15}: cdwx
			·  │└yzbc ->DFA{4,5,13,14,15}: cdwx
			·  └d●->DFA{16}: 100
		`))
	})
})

var _ = Describe("GraphVizString", func() {
	It("is initially empty", func() {
		result := dfa.Dfa("", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				label="//";
				subgraph nfa {
					node [shape=record];
					nfa:n1:ne -> nfa:n2:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa [label="{<n0>0|fail|}|{<n1>1|nop|2}|{<n2>2|match|}"];
				}
				"1,2" [shape=doublecircle];
			}
		`))
	})

	It("branching paths", func() {
		result := dfa.Dfa("abc|acd|xyz", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				label="/abc|acd|xyz/";
				subgraph nfa {
					node [shape=record];
					nfa:n1:ne -> nfa:n6:n [labeldistance=2 headlabel="a"];
					nfa:n2:ne -> nfa:n3:n [labeldistance=2 headlabel="b"];
					nfa:n3:ne -> nfa:n11:n [labeldistance=2 headlabel="c"];
					nfa:n4:ne -> nfa:n5:n [labeldistance=2 headlabel="c"];
					nfa:n5:ne -> nfa:n11:n [labeldistance=2 headlabel="d"];
					nfa:n6:ne -> nfa:n2:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n6:ne -> nfa:n4:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n7:ne -> nfa:n8:n [labeldistance=2 headlabel="x"];
					nfa:n8:ne -> nfa:n9:n [labeldistance=2 headlabel="y"];
					nfa:n9:ne -> nfa:n11:n [labeldistance=2 headlabel="z"];
					nfa:n10:ne -> nfa:n1:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n10:ne -> nfa:n7:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa [label="{<n0>0|fail|}|{<n1>1|rune1 'a'|6}|{<n2>2|rune1 'b'|3}|{<n3>3|rune1 'c'|11}|{<n4>4|rune1 'c'|5}|{<n5>5|rune1 'd'|11}|{<n6>6|alt|2, 4}|{<n7>7|rune1 'x'|8}|{<n8>8|rune1 'y'|9}|{<n9>9|rune1 'z'|11}|{<n10>10|alt|1, 7}|{<n11>11|match|}"];
				}
				// 1,7,10 does not match
				"1,7,10" -> "2,4,6" [label="a"];
				// 2,4,6 does not match
				"2,4,6" -> "3" [label="b"];
				// 3 does not match
				"3" -> "11" [label="c"];
				"11" [shape=doublecircle];
				"2,4,6" -> "5" [label="c"];
				// 5 does not match
				"5" -> "11" [label="d"];
				"1,7,10" -> "8" [label="x"];
				// 8 does not match
				"8" -> "9" [label="y"];
				// 9 does not match
				"9" -> "11" [label="z"];
			}
		`))
	})

	It("looping paths", func() {
		result := dfa.Dfa("[ab]+", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				label="/[ab]+/";
				subgraph nfa {
					node [shape=record];
					nfa:n1:ne -> nfa:n2:n [labeldistance=2 headlabel="ab"];
					nfa:n2:ne -> nfa:n1:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n2:ne -> nfa:n3:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa [label="{<n0>0|fail|}|{<n1>1|rune 'ab'|2}|{<n2>2|alt|1, 3}|{<n3>3|match|}"];
				}
				// 1 does not match
				"1" -> "1,2,3" [label="[ab]"];
				"1,2,3" [shape=doublecircle];
				"1,2,3" -> "1,2,3" [label="[ab]"];
			}
		`))
	})

	It("dfa example online", func() {
		result := dfa.Dfa("(a|b)*ab", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				label="/(a|b)*ab/";
				subgraph nfa {
					node [shape=record];
					nfa:n1:ne -> nfa:n2:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n2:ne -> nfa:n3:n [labeldistance=2 headlabel="ab"];
					nfa:n3:ne -> nfa:n4:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n4:ne -> nfa:n1:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n4:ne -> nfa:n5:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n5:ne -> nfa:n6:n [labeldistance=2 headlabel="a"];
					nfa:n6:ne -> nfa:n7:n [labeldistance=2 headlabel="b"];
					nfa [label="{<n0>0|fail|}|{<n1>1|cap 2|2}|{<n2>2|rune 'ab'|3}|{<n3>3|cap 3|4}|{<n4>4|alt|1, 5}|{<n5>5|rune1 'a'|6}|{<n6>6|rune1 'b'|7}|{<n7>7|match|}"];
				}
				// 1,2,4,5 does not match
				"1,2,4,5" -> "1,2,3,4,5,6" [label="a"];
				// 1,2,3,4,5,6 does not match
				"1,2,3,4,5,6" -> "1,2,3,4,5,6" [label="a"];
				"1,2,3,4,5,6" -> "1,2,3,4,5,7" [label="b"];
				"1,2,3,4,5,7" [shape=doublecircle];
				"1,2,3,4,5,7" -> "1,2,3,4,5,6" [label="a"];
				"1,2,3,4,5,7" -> "1,2,3,4,5" [label="b"];
				// 1,2,3,4,5 does not match
				"1,2,3,4,5" -> "1,2,3,4,5,6" [label="a"];
				"1,2,3,4,5" -> "1,2,3,4,5" [label="b"];
				"1,2,4,5" -> "1,2,3,4,5" [label="b"];
			}
		`))
	})

	It("dfa example online (variant)", func() {
		result := dfa.Dfa("(a|b)*ba", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				label="/(a|b)*ba/";
				subgraph nfa {
					node [shape=record];
					nfa:n1:ne -> nfa:n2:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n2:ne -> nfa:n3:n [labeldistance=2 headlabel="ab"];
					nfa:n3:ne -> nfa:n4:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n4:ne -> nfa:n1:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n4:ne -> nfa:n5:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n5:ne -> nfa:n6:n [labeldistance=2 headlabel="b"];
					nfa:n6:ne -> nfa:n7:n [labeldistance=2 headlabel="a"];
					nfa [label="{<n0>0|fail|}|{<n1>1|cap 2|2}|{<n2>2|rune 'ab'|3}|{<n3>3|cap 3|4}|{<n4>4|alt|1, 5}|{<n5>5|rune1 'b'|6}|{<n6>6|rune1 'a'|7}|{<n7>7|match|}"];
				}
				// 1,2,4,5 does not match
				"1,2,4,5" -> "1,2,3,4,5" [label="a"];
				// 1,2,3,4,5 does not match
				"1,2,3,4,5" -> "1,2,3,4,5" [label="a"];
				"1,2,3,4,5" -> "1,2,3,4,5,6" [label="b"];
				// 1,2,3,4,5,6 does not match
				"1,2,3,4,5,6" -> "1,2,3,4,5,7" [label="a"];
				"1,2,3,4,5,7" [shape=doublecircle];
				"1,2,3,4,5,7" -> "1,2,3,4,5" [label="a"];
				"1,2,3,4,5,7" -> "1,2,3,4,5,6" [label="b"];
				"1,2,3,4,5,6" -> "1,2,3,4,5,6" [label="b"];
				"1,2,4,5" -> "1,2,3,4,5,6" [label="b"];
			}
		`))
	})

	It("provider masks within a cycle", func() {
		result := dfa.Dfa("a(?:(?:bcwyz)*b)(?:cwx)*cd", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				label="/a(?:(?:bcwyz)*b)(?:cwx)*cd/";
				subgraph nfa {
					node [shape=record];
					nfa:n1:ne -> nfa:n7:n [labeldistance=2 headlabel="a"];
					nfa:n2:ne -> nfa:n3:n [labeldistance=2 headlabel="b"];
					nfa:n3:ne -> nfa:n4:n [labeldistance=2 headlabel="c"];
					nfa:n4:ne -> nfa:n5:n [labeldistance=2 headlabel="w"];
					nfa:n5:ne -> nfa:n6:n [labeldistance=2 headlabel="y"];
					nfa:n6:ne -> nfa:n7:n [labeldistance=2 headlabel="z"];
					nfa:n7:ne -> nfa:n2:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n7:ne -> nfa:n8:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n8:ne -> nfa:n12:n [labeldistance=2 headlabel="b"];
					nfa:n9:ne -> nfa:n10:n [labeldistance=2 headlabel="c"];
					nfa:n10:ne -> nfa:n11:n [labeldistance=2 headlabel="w"];
					nfa:n11:ne -> nfa:n12:n [labeldistance=2 headlabel="x"];
					nfa:n12:ne -> nfa:n9:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n12:ne -> nfa:n13:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n13:ne -> nfa:n14:n [labeldistance=2 headlabel="c"];
					nfa:n14:ne -> nfa:n15:n [labeldistance=2 headlabel="d"];
					nfa [label="{<n0>0|fail|}|{<n1>1|rune1 'a'|7}|{<n2>2|rune1 'b'|3}|{<n3>3|rune1 'c'|4}|{<n4>4|rune1 'w'|5}|{<n5>5|rune1 'y'|6}|{<n6>6|rune1 'z'|7}|{<n7>7|alt|2, 8}|{<n8>8|rune1 'b'|12}|{<n9>9|rune1 'c'|10}|{<n10>10|rune1 'w'|11}|{<n11>11|rune1 'x'|12}|{<n12>12|alt|9, 13}|{<n13>13|rune1 'c'|14}|{<n14>14|rune1 'd'|15}|{<n15>15|match|}"];
				}
				// 1 does not match
				"1" -> "2,7,8" [label="a"];
				// 2,7,8 does not match
				"2,7,8" -> "3,9,12,13" [label="b"];
				// 3,9,12,13 does not match
				"3,9,12,13" -> "4,10,14" [label="c"];
				// 4,10,14 does not match
				"4,10,14" -> "15" [label="d"];
				"15" [shape=doublecircle];
				"4,10,14" -> "5,11" [label="w"];
				// 5,11 does not match
				"5,11" -> "6" [label="y"];
				// 6 does not match
				"6" -> "2,7,8" [label="z"];
				"5,11" -> "9,12,13" [label="x"];
				// 9,12,13 does not match
				"9,12,13" -> "10,14" [label="c"];
				// 10,14 does not match
				"10,14" -> "11" [label="w"];
				// 11 does not match
				"11" -> "9,12,13" [label="x"];
				"10,14" -> "15" [label="d"];
			}
		`))
	})

	It("all letters are optional", func() {
		result := dfa.Dfa("a?b?c?d?", 1.0)
		Expect(result.GraphVizString()).To(matchers.LookLike(`
			digraph G {
				label="/a?b?c?d?/";
				subgraph nfa {
					node [shape=record];
					nfa:n1:ne -> nfa:n4:n [labeldistance=2 headlabel="a"];
					nfa:n2:ne -> nfa:n1:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n2:ne -> nfa:n4:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n3:ne -> nfa:n6:n [labeldistance=2 headlabel="b"];
					nfa:n4:ne -> nfa:n3:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n4:ne -> nfa:n6:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n5:ne -> nfa:n8:n [labeldistance=2 headlabel="c"];
					nfa:n6:ne -> nfa:n5:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n6:ne -> nfa:n8:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n7:ne -> nfa:n9:n [labeldistance=2 headlabel="d"];
					nfa:n8:ne -> nfa:n7:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa:n8:ne -> nfa:n9:n [labeldistance=2 headlabel="ε" style=dotted];
					nfa [label="{<n0>0|fail|}|{<n1>1|rune1 'a'|4}|{<n2>2|alt|1, 4}|{<n3>3|rune1 'b'|6}|{<n4>4|alt|3, 6}|{<n5>5|rune1 'c'|8}|{<n6>6|alt|5, 8}|{<n7>7|rune1 'd'|9}|{<n8>8|alt|7, 9}|{<n9>9|match|}"];
				}
				"1,2,3,4,5,6,7,8,9" [shape=doublecircle];
				"1,2,3,4,5,6,7,8,9" -> "3,4,5,6,7,8,9" [label="a"];
				"3,4,5,6,7,8,9" [shape=doublecircle];
				"3,4,5,6,7,8,9" -> "5,6,7,8,9" [label="b"];
				"5,6,7,8,9" [shape=doublecircle];
				"5,6,7,8,9" -> "7,8,9" [label="c"];
				"7,8,9" [shape=doublecircle];
				"7,8,9" -> "9" [label="d"];
				"9" [shape=doublecircle];
				"5,6,7,8,9" -> "9" [label="d"];
				"3,4,5,6,7,8,9" -> "7,8,9" [label="c"];
				"3,4,5,6,7,8,9" -> "9" [label="d"];
				"1,2,3,4,5,6,7,8,9" -> "5,6,7,8,9" [label="b"];
				"1,2,3,4,5,6,7,8,9" -> "7,8,9" [label="c"];
				"1,2,3,4,5,6,7,8,9" -> "9" [label="d"];
			}
		`))
	})
})

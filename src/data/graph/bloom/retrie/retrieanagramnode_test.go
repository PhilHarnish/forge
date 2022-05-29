package retrie_test

import (
	"strings"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie"
)

type proxyNodeIterator struct {
	node.NodeIterator
	iterations int
}

func (node *proxyNodeIterator) Items(generator node.NodeGenerator) node.NodeItems {
	node.iterations++
	return generator.Items(node.NodeIterator)
}

var _ = Describe("Anagram syntax", func() {
	It("matches simple <anagram> pattern", func() {
		trie := retrie.NewReTrie(`<abc>`, 1.0)
		Expect(debug.StringChildren(trie, 5)).To(matchers.LookLike(`
				ReTrie: ABC
				│◌◌◌●
				├a ->ReTrieAnagram: BC
				││◌◌●
				│├b ->ReTrieAnagram: C
				│││◌●
				││└c●->ReTrie: 100
				│└c ->ReTrieAnagram: B
				│ │◌●
				│ └b●->ReTrie: 100
				├b ->ReTrieAnagram: AC
				││◌◌●
				│├a ->ReTrieAnagram: C
				│││◌●
				││└c●->ReTrie: 100
				│└c ->ReTrieAnagram: A
				│ │◌●
				│ └a●->ReTrie: 100
				└c ->ReTrieAnagram: AB
				·│◌◌●
				·├a ->ReTrieAnagram: B
				·││◌●
				·│└b●->ReTrie: 100
				·└b ->ReTrieAnagram: A
				· │◌●
				· └a●->ReTrie: 100
		`))
	})

	It("matches <anagram> pattern", func() {
		trie := retrie.NewReTrie(`a<xy>(bbbb)`, 1.0)
		Expect(trie.Labels()).To(Equal([]string{"1"}))
		Expect(debug.StringChildren(trie, 5)).To(matchers.LookLike(`
			ReTrie: ABXY
			│◌◌◌◌◌◌◌●
			└a ->ReTrie: BXY
			·│◌◌◌◌◌◌●
			·├x ->ReTrieAnagram: BY
			·││◌◌◌◌◌●
			·│└y ->ReTrie: B
			·│ │Subscribe(ReTrieItems[0])
			·│ │◌◌◌◌●
			·│ └bbbb●->ReTrie: 100
			·│      Subscribe(ReTrieItems[1])
			·└y ->ReTrieAnagram: BX
			· │◌◌◌◌◌●
			· └x ->ReTrie: B
			·  │Subscribe(ReTrieItems[0])
			·  │◌◌◌◌●
			·  └bbbb●->ReTrie: 100
			·       Subscribe(ReTrieItems[1])
		`))
	})

	It("matches <anagram>{x,y} pattern", func() {
		trie := retrie.NewReTrie(`<ab>{1,2}`, 1.0)
		Expect(debug.StringChildren(trie, 5)).To(matchers.LookLike(`
			ReTrie: AB
			│◌◌●◌●
			├a ->ReTrieAnagram: aB
			││◌●◌●
			│└b●->ReTrie: 100 AB
			│ │●◌●
			│ ├a ->ReTrieAnagram: B
			│ ││◌●
			│ │└b●->ReTrie: 100
			│ └b ->ReTrieAnagram: A
			│  │◌●
			│  └a●->ReTrie: 100
			└b ->ReTrieAnagram: Ab
			·│◌●◌●
			·└a●->ReTrie: 100 AB
			· │●◌●
			· ├a ->ReTrieAnagram: B
			· ││◌●
			· │└b●->ReTrie: 100
			· └b ->ReTrieAnagram: A
			·  │◌●
			·  └a●->ReTrie: 100
		`))
	})

	It("supports anagrams of regular expressions: character ranges", func() {
		trie := retrie.NewReTrie(`<([ab])([bc])>`, 1.0)
		Expect(debug.StringChildren(trie, 5)).To(matchers.LookLike(`
			ReTrie: abc
			│Subscribe(ReTrieItems[0 2])
			│◌◌●
			├a ->ReTrieAnagram: bc
			││Subscribe(ReTrieItems[1])
			││◌●
			│├b●->ReTrie: 100
			││ Subscribe(ReTrieItems[1 3])
			│└c●->ReTrie: 100
			│  Subscribe(ReTrieItems[1 3])
			├b ->((ReTrieAnagram: bc) || (ReTrieAnagram: ab)): abc
			││Subscribe(ReTrieItems[1 3])
			││◌●
			│├a●->ReTrie: 100
			││ Subscribe(ReTrieItems[1 3])
			│├b●->((ReTrie: 100) || (ReTrie: 100)): 100
			│└c●->ReTrie: 100
			│  Subscribe(ReTrieItems[1 3])
			└c ->ReTrieAnagram: ab
			·│Subscribe(ReTrieItems[3])
			·│◌●
			·├a●->ReTrie: 100
			·│ Subscribe(ReTrieItems[1 3])
			·└b●->ReTrie: 100
			·  Subscribe(ReTrieItems[1 3])
		`))
	})

	It("supports ambiguous anagrams", func() {
		trie := retrie.NewReTrie(`<(a?b?c?)(abc)>`, 1.0)
		Expect(debug.StringPath(trie, "abc")).To(matchers.LookLike(`
			ReTrie: ABC
			│Subscribe(ReTrieItems[0 1 2])
			│◌◌◌●●●●
			├a ->ReTrie: aBC
			││Subscribe(ReTrieItems[1])
			││◌◌●●●●
			│├abc●->ReTrie: 100
			│├b ->ReTrie: abC
			│││Subscribe(ReTrieItems[1])
			│││◌●●●●
			││├abc●->ReTrie: 100
			││└c●->((ReTrieAnagram: 100 abc) || (ReTrieAnagram: ABC)): 100 abc
			││ └1 children: a
			│└c ->ReTrieAnagram: ABC
			│ └1 children: a
			├b ->ReTrie: ABC
			│└2 children: ac
			└c ->ReTrie: ABC
			·└1 children: a
		`))
	})

	It("supports optional anagrams", func() {
		trie := retrie.NewReTrie(`a<(b?)(c?)>?d`, 1.0)
		Expect(debug.StringChildren(trie, 5)).To(matchers.LookLike(`
			ReTrie: AbcD
			│◌◌●●●
			└a ->ReTrie: bcD
			·│Subscribe(ReTrieItems[0 1 2 3])
			·│◌●●●
			·├b ->ReTrie: cD
			·││Subscribe(ReTrieItems[1 3])
			·││◌●●
			·│├c ->ReTrie: D
			·│││Subscribe(ReTrieItems[1 3])
			·│││◌●
			·││└d●->ReTrie: 100
			·│└d●->ReTrie: 100
			·├c ->ReTrie: bD
			·││Subscribe(ReTrieItems[1 3])
			·││◌●●
			·│├b ->ReTrie: D
			·│││Subscribe(ReTrieItems[1 3])
			·│││◌●
			·││└d●->ReTrie: 100
			·│└d●->ReTrie: 100
			·└d●->ReTrie: 100
		`))
	})

	Describe("benchmarks", func() {
		var child *proxyNodeIterator
		BeforeEach(func() {
			child = &proxyNodeIterator{
				NodeIterator: node.NewNode(1.0),
			}
			retrie.Register("child", child)
		})

		AfterEach(func() {
			retrie.ClearRegistry()
		})

		It("should expand everything", func() {
			trie := retrie.NewReTrie(`<abcde>{child}`, 1.0)
			newlines := strings.Count(debug.StringChildren(trie, 999), "\n")
			Expect(newlines).To(BeNumerically(">=", 5*4*3*2*1))
		})
	})
})

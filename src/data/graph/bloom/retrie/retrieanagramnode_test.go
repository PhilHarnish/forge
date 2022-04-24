package retrie_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie"
)

var _ = Describe("Special syntax", func() {
	It("matches simple <anagram> pattern", func() {
		trie := retrie.NewReTrie(`<abc>`, 1.0)
		Expect(node.StringChildren(trie, 5)).To(matchers.LookLike(`
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
		Expect(node.StringChildren(trie, 5)).To(matchers.LookLike(`
				ReTrie: ABXY
				│◌◌◌◌◌◌◌●
				└a ->ReTrie: BXY
				·│◌◌◌◌◌◌●
				·├x ->ReTrieAnagram: BY
				·││◌◌◌◌◌●
				·│└y ->ReTrie: B
				·│ │◌◌◌◌●
				·│ └bbbb●->ReTrie: 100
				·└y ->ReTrieAnagram: BX
				· │◌◌◌◌◌●
				· └x ->ReTrie: B
				·  │◌◌◌◌●
				·  └bbbb●->ReTrie: 100
		`))
	})

	XIt("matches <anagram>{x,y} pattern", func() {
		trie := retrie.NewReTrie(`<ab>{1,2}`, 1.0)
		Expect(node.StringChildren(trie, 5)).To(matchers.LookLike(`
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
})

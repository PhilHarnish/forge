package retrie_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie"
)

type proxyNodeIterator struct {
	node.NodeIterator
	iterations int
}

func (node *proxyNodeIterator) Items(acceptor node.NodeAcceptor) node.NodeItems {
	node.iterations++
	return node.NodeIterator.Items(acceptor)
}

var _ = Describe("Anagram syntax", func() {
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

	It("matches <anagram>{x,y} pattern", func() {
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

	It("supports anagrams of regular expressions: character ranges", func() {
		trie := retrie.NewReTrie(`<([ab])([bc])>`, 1.0)
		Expect(node.StringChildren(trie, 5)).To(matchers.LookLike(`
				ReTrie: abc
				│◌◌●
				├a ->ReTrie: bc
				││◌●
				│├b●->ReTrie: 100
				│└c●->ReTrie: 100
				├b ->ReTrie: abc
				││◌●
				│├c●->ReTrie: 100
				│├a●->ReTrie: 100
				│└b●->ReTrie: 100
				└c ->ReTrie: ab
				·│◌●
				·├a●->ReTrie: 100
				·└b●->ReTrie: 100
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
			node.StringChildren(trie, 999)
			Expect(child.iterations).To(Equal(5 * 4 * 3 * 2 * 1))
		})
	})
})

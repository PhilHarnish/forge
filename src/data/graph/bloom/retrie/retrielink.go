package retrie

import (
	"container/heap"
	"unicode/utf8"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
)

type reTrieLink struct {
	prefix   string
	runes    []rune
	node     *reTrieNode
	edgeMask mask.Mask
}

func newReTrieLink(runes []rune, node *reTrieNode, edgeMask mask.Mask) *reTrieLink {
	return &reTrieLink{
		runes:    runes,
		node:     node,
		edgeMask: edgeMask,
	}
}

func newReTrieLinkFromRunes(runes []rune, node *reTrieNode) *reTrieLink {
	edgeMask, err := mask.AlphabetMaskRanges(runes)
	if err != nil {
		panic(err)
	}
	return newReTrieLink(runes, node, edgeMask)
}

func newReTrieLinkForPrefix(prefix string, node *reTrieNode) *reTrieLink {
	prefixRune, _ := utf8.DecodeRuneInString(prefix)
	edgeMask, _ := mask.AlphabetMask(prefixRune)
	return &reTrieLink{
		prefix:   prefix,
		runes:    []rune{prefixRune, prefixRune},
		node:     node,
		edgeMask: edgeMask,
	}
}

type reTrieLinkList []*reTrieLink

func (edges reTrieLinkList) Len() int {
	return len(edges)
}

func (edges reTrieLinkList) Less(i int, j int) bool {
	if edges[i].runes[0] == edges[j].runes[0] {
		return edges[i].runes[1] < edges[j].runes[1]
	}
	return edges[i].runes[0] < edges[j].runes[0]
}

func (h reTrieLinkList) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *reTrieLinkList) Push(item interface{}) {
	*h = append(*h, item.(*reTrieLink))
}

func (h *reTrieLinkList) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *reTrieLinkList) Next() *reTrieLink {
	return heap.Pop(h).(*reTrieLink)
}

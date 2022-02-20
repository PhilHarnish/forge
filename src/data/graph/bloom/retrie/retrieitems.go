package retrie

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type reTrieItems struct {
	acceptor   node.NodeAcceptor
	root       *reTrieNode
	index      int
	runeIndex  int
	runeOffset rune
}

func newTrieItems(acceptor node.NodeAcceptor, root *reTrieNode) *reTrieItems {
	return &reTrieItems{
		acceptor: acceptor,
		root:     root,
	}
}

func (items *reTrieItems) HasNext() bool {
	return items.index < len(items.root.links)
}

func (items *reTrieItems) Next() (string, node.NodeIterator) {
	link := items.root.links[items.index]
	if link.runes == nil {
		items.index++
		return link.prefix, link.node
	}
	prefix := string(link.runes[items.runeIndex] + items.runeOffset)
	maxOffset := link.runes[items.runeIndex+1] - link.runes[items.runeIndex]
	items.runeOffset++
	if items.runeOffset > maxOffset {
		items.runeOffset = 0
		items.runeIndex += 2
	}
	if items.runeIndex >= len(link.runes) {
		items.runeIndex = 0
		items.index++
	}
	return prefix, link.node
}

package retrie

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type reTrieItems struct {
	generator  node.NodeGenerator
	root       *reTrieNode
	index      int
	runeIndex  int
	runeOffset rune
}

func newTrieItems(generator node.NodeGenerator, root *reTrieNode) node.NodeItems {
	result := &reTrieItems{
		generator: generator,
		root:      root,
	}
	if len(root.captures) > 0 {
		generator.Subscribe(result)
	}
	return result
}

func (items *reTrieItems) HasNext() bool {
	return items.index < len(items.root.links)
}

func (items *reTrieItems) Next() (string, node.NodeIterator) {
	link := items.root.links[items.index]
	if link.prefix != "" {
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

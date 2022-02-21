package retrie

import (
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type reTrieItems struct {
	acceptor   node.NodeAcceptor
	root       *reTrieNode
	index      int
	runeIndex  int
	runeOffset rune
}

const DOT_PREFIX = "."
const OPTIONAL_PREFIX = "?"

func newTrieItems(acceptor node.NodeAcceptor, root *reTrieNode) node.NodeItems {
	if len(root.links) == 1 && root.links[0].prefix == OPTIONAL_PREFIX {
		// The "?" operator has zero length so iterate that node directly.
		return root.links[0].node.Items(acceptor)
	}
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
	if link.prefix == OPTIONAL_PREFIX {
		panic("Optional iteration should happen before reaching this point.")
	} else if link.prefix == DOT_PREFIX {
		prefix := string(mask.ALPHABET[items.runeIndex])
		items.runeIndex++
		if items.runeIndex >= mask.SIZE {
			items.index++
		}
		return prefix, link.node
	} else if link.runes == nil {
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

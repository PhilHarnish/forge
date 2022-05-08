package trie

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type trieItems struct {
	generator node.NodeGenerator
	root      *Trie
	index     int
}

func newTrieItems(generator node.NodeGenerator, trie *Trie) *trieItems {
	return &trieItems{
		generator: generator,
		root:      trie,
		index:     0,
	}
}

func (items *trieItems) HasNext() bool {
	return items.index < len(items.root.links)
}

func (items *trieItems) Next() (string, node.NodeIterator) {
	for items.HasNext() {
		link := items.root.links[items.index]
		items.index++
		if items.generator(link.prefix, link.node.Node) > 0 {
			return link.prefix, link.node
		}
	}
	return "", nil
}

package trie

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type iteratorItems struct {
	acceptor node.NodeAcceptor
	root     *Trie
	index    int
}

func newIteratorItems(acceptor node.NodeAcceptor, trie *Trie) *iteratorItems {
	return &iteratorItems{
		acceptor: acceptor,
		root:     trie,
		index:    0,
	}
}

func (items *iteratorItems) Next() (string, node.NodeIterator) {
	if items.index >= len(items.root.links) {
		return "", nil
	}
	link := items.root.links[items.index]
	items.index++
	return link.prefix, link.node
}

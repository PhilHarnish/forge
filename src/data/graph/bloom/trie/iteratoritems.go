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

func (items *iteratorItems) HasNext() bool {
	return items.index < len(items.root.links)
}

func (items *iteratorItems) Next() (string, node.NodeIterator) {
	for items.HasNext() {
		link := items.root.links[items.index]
		items.index++
		if items.acceptor(link.prefix, &link.node.Node) > 0 {
			return link.prefix, link.node
		}
	}
	return "", nil
}

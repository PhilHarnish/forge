package retrie

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type reTrieItems struct {
	acceptor node.NodeAcceptor
	root     *reTrieNode
	index    int
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
	items.index++
	return link.prefix, link.node
}

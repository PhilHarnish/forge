package trie

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type iteratorItems struct {
	acceptor node.NodeAcceptor
	root     *Trie
}

func newIteratorItems(acceptor node.NodeAcceptor, trie *Trie) *iteratorItems {
	return &iteratorItems{
		acceptor: acceptor,
		root:     trie,
	}
}

func (items *iteratorItems) Next() (string, *node.Node) {
	return "", nil
}

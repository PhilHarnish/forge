package op

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type operatorItems struct {
	acceptor node.NodeAcceptor
	operator Operation
}

func (items *operatorItems) HasNext() bool {
	return false
}

func (items *operatorItems) Next() (string, node.NodeIterator) {
	return "", nil
}

package null

import "github.com/philharnish/forge/src/data/graph/bloom/node"

var nullNode = node.NewNode(0.0)

type null struct{}

var Null = &null{}

func (root *null) Root() *node.Node {
	return nullNode
}

func (root *null) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return root
}

func (root *null) HasNext() bool {
	return false
}

func (root *null) Next() (string, node.NodeIterator) {
	panic("Null has no children")
}

func (root *null) String() string {
	return node.Format("Null", root.Root())
}

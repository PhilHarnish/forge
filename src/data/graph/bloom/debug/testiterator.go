package debug

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type TestIterator struct {
	root  *node.Node
	items *TestItems
}

func NewTestIterator(root *node.Node, items *TestItems) *TestIterator {
	return &TestIterator{
		root:  root,
		items: items,
	}
}

func (iterator *TestIterator) Root() *node.Node {
	if iterator.root == nil {
		return node.NewNode(1.0)
	}
	return iterator.root
}

func (iterator *TestIterator) Items(acceptor node.NodeAcceptor) node.NodeItems {
	result := &TestItems{}
	if len(*iterator.items) > 0 {
		*result = append(*result, *iterator.items...)
	}
	return result
}

func (iterator *TestIterator) String() string {
	return node.Format("TestIterator", iterator.Root())
}

type TestItems []string

func (items *TestItems) HasNext() bool {
	return len(*items) > 0
}

func (items *TestItems) Next() (string, node.NodeIterator) {
	if !items.HasNext() {
		return "", nil
	}
	original := items
	item := (*items)[0]
	*items = (*items)[1:]
	return item, &TestIterator{
		root:  node.NewNode(),
		items: original,
	}
}

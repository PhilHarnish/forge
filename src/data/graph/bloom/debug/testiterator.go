package debug

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
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
	return iterator.root
}

func (iterator *TestIterator) Items(generator node.NodeGenerator) node.NodeItems {
	result := &TestItems{}
	if len(*iterator.items) > 0 {
		*result = append(*result, *iterator.items...)
	}
	return result
}

func (iterator *TestIterator) String() string {
	return node.Format("TestIterator", iterator.Root())
}

type TestItems []weight.WeightedString

func (items *TestItems) HasNext() bool {
	return len(*items) > 0
}

func (items *TestItems) Next() (string, node.NodeIterator) {
	if !items.HasNext() {
		panic("TestIterator exhausted")
	}
	original := items
	item := (*items)[0]
	*items = (*items)[1:]
	root := node.NewNode()
	if item.Weight > 0 {
		root.Match(item.Weight)
	}
	return item.String, &TestIterator{
		root:  root,
		items: original,
	}
}

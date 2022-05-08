package span

import (
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type span struct {
	node  *node.Node
	child node.NodeIterator
	path  string
}

type spanItems struct {
	span *span
}

func NewSpan(path string, destination ...node.NodeIterator) *span {
	result := &span{
		node: node.NewNode(),
		path: path,
	}
	if len(destination) == 0 {
		result.child = node.NewNode()
	} else if len(destination) == 1 {
		result.child = destination[0]
	} else {
		panic(fmt.Sprintf("invalid arguments %v", destination))
	}
	result.node.MaskPathToChild(path, result.child.Root())
	return result
}

func (root *span) Root() *node.Node {
	return root.node
}

func (root *span) Items(generator node.NodeGenerator) node.NodeItems {
	return &spanItems{span: root}
}

func (items *spanItems) HasNext() bool {
	return items.span != nil
}

func (items *spanItems) Next() (string, node.NodeIterator) {
	path := items.span.path
	child := items.span.child
	items.span = nil
	return path, child
}

func (root *span) String() string {
	return fmt.Sprintf("Span: '%s'->%s", root.path, root.child.String())
}

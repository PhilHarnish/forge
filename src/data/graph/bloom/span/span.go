package span

import (
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/null"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type span struct {
	*node.Node
	path string
}

type spanItems struct {
	span *span
}

func NewSpan(path string, matchWeight ...weight.Weight) *span {
	return &span{
		Node: node.NewNode(matchWeight...),
		path: path,
	}
}

func (root *span) Root() *node.Node {
	return root.Node
}

func (root *span) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return &spanItems{span: root}
}

func (items *spanItems) HasNext() bool {
	return items.span != nil
}

func (items *spanItems) Next() (string, node.NodeIterator) {
	path := items.span.path
	items.span = nil
	return path, null.Null
}

func (root *span) String() string {
	return fmt.Sprintf("Span('%s', %.2g)", root.path, root.MatchWeight)
}

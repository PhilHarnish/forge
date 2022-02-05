package node

import (
	"fmt"
	"strings"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type Node struct {
	// Non-zero when this node is a match.
	MatchWeight weight.Weight
	// Maximum weight for outgoing edges.
	MaxWeight weight.Weight
	// BitMask for outgoing edges.
	ProvideMask mask.Mask
	// BitMask for edges which lead to matching Nodes.
	RequireMask mask.Mask
	// BitMask for distances matching Nodes.
	LengthsMask mask.Mask
}

type NodeIterator interface {
	Items(acceptor NodeAcceptor) NodeItems
	Root() *Node
	String() string
}

type NodeItems interface {
	HasNext() bool
	Next() (string, NodeIterator)
}

// Evaluate the `Weight` for a `node` at `path`.
// Typically, when the result is non-zero the caller should immediately
// return Cursor{node, path}
type NodeAcceptor = func(path string, node *Node) weight.Weight

func NodeAcceptAll(path string, node *Node) weight.Weight {
	return 1.0
}

func NodeAcceptNone(path string, node *Node) weight.Weight {
	return 0.0
}

func (node *Node) String() string {
	return Format("Node", node)
}

func Format(name string, node *Node) string {
	return fmt.Sprintf(
		"%s('%s', '%s', %.2g)",
		name,
		mask.MaskString(node.ProvideMask, node.RequireMask),
		mask.LengthString(node.LengthsMask),
		node.MatchWeight,
	)
}

func StringChildren(iterator NodeIterator) string {
	results := []string{
		iterator.String(),
	}
	items := iterator.Items(NodeAcceptAll)
	for items.HasNext() {
		path, item := items.Next()
		results = append(results, fmt.Sprintf("%s = %s", path, item.String()))
	}
	return strings.Join(results, "\n")
}

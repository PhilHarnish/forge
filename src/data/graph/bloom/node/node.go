package node

import (
	"fmt"

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
}

type NodeItems interface {
	Next() (string, *Node)
}

// Evaluate the `Weight` for a `node` at `path`.
// Typically, when the result is non-zero the caller should immediately
// return Cursor{node, path}
type NodeAcceptor = func(path string, node *Node) weight.Weight

func (node *Node) String() string {
	return Format("Node", node)
}

func Format(name string, node *Node) string {
	return fmt.Sprintf(
		"%s('%s', '%s', %.2g)",
		name,
		mask.MaskAlphabet(node.ProvideMask, node.RequireMask),
		mask.LengthAlphabet(node.LengthsMask),
		node.MatchWeight,
	)
}

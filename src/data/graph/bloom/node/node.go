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

func NewNode() *Node {
	return &Node{
		MatchWeight: weight.Weight(0),
		MaxWeight:   weight.Weight(0),
		ProvideMask: mask.Mask(0b0),
		RequireMask: mask.UNSET,
		LengthsMask: mask.Mask(0b0),
	}
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

func StringChildren(iterator NodeIterator, depth ...int) string {
	if len(depth) > 0 {
		return stringChildrenWithPrefix(iterator, "", depth[0])
	}
	return stringChildrenWithPrefix(iterator, "", 1)
}

func stringChildrenWithPrefix(iterator NodeIterator, base string, remaining int) string {
	if remaining == 0 {
		return iterator.String()
	}
	results := []string{
		iterator.String(),
	}
	items := iterator.Items(NodeAcceptAll)
	for items.HasNext() {
		path, item := items.Next()
		line := "├─"
		prefix := "│ "
		if !items.HasNext() {
			line = "└─"
			prefix = "• "
		}
		results = append(results, fmt.Sprintf("%s%s = %s",
			base+line, path, stringChildrenWithPrefix(item, base+prefix, remaining-1)))

	}
	return strings.Join(results, "\n")
}

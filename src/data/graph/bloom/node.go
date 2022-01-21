package bloom

import (
	"fmt"
	"math"
)

type Weight = float64

// Graph node with bloom-filter style optimizations.
type Node struct {
	// Non-zero when this node is a match.
	matchWeight Weight
	// Maximum weight for outgoing edges.
	maxWeight Weight
	// BitMask for outgoing edges.
	provideMask BitMask
	// BitMask for edges which lead to matching Nodes.
	requireMask BitMask
	// BitMask for distances matching Nodes.
	lengthsMask BitMask
	// Array of outgoing Nodes (index assigned by Position from mask.go).
	links *[SIZE]*nodeLink
}

type nodeLink struct {
	prefix string
	node   *Node
}

func NewNode(matchWeight ...Weight) *Node {
	result := Node{}
	result.requireMask = UNSET
	if len(matchWeight) == 1 {
		result.Match(matchWeight[0])
	}
	return &result
}

func (node *Node) Match(weight Weight) {
	if node.matchWeight != 0.0 {
		panic(fmt.Errorf("duplicate attempts to set match weight (%f and %f)",
			node.matchWeight, weight))
	}
	node.matchWeight = weight
	node.lengthsMask |= 0b1 // Match at current position
	node.Weight(weight)
}

func (node *Node) Weight(weight Weight) {
	node.maxWeight = math.Max(node.maxWeight, weight)
}

func (node *Node) Link(edge string, child *Node) error {
	if len(edge) == 0 {
		return fmt.Errorf("attempted to link empty key")
	}
	if node.links == nil {
		node.links = &[SIZE]*nodeLink{}
	}
	c := edge[0]
	prefix := edge[1:]
	position, err := Position(rune(c))
	if err != nil {
		return fmt.Errorf("error while linking: %w", err)
	}
	edgeMask := BitMask(1 << position)
	if len(edge) > 1 {
		return fmt.Errorf("multi-byte keys are currently unsupported")
	}
	// Inherit maxWeight.
	node.Weight(child.maxWeight)
	// Provide anything ANY children provides (including the edge itself).
	node.provideMask |= edgeMask | BitMask(child.provideMask)
	if child.requireMask == UNSET {
		// Ignore the child's require mask if it is UNSET.
		node.requireMask &= edgeMask
	} else {
		// Require anything ALL children requires (including the edge itself).
		node.requireMask &= edgeMask | BitMask(child.requireMask)
	}
	// Inherit matching lengths.
	node.lengthsMask |= child.lengthsMask << len(edge)
	if node.links[position] == nil {
		// New link.
		node.links[position] = &nodeLink{
			prefix,
			child,
		}
		return nil
	} else if node.links[position].prefix == prefix {
		// Proposed link already exists.
		return fmt.Errorf("link '%s' already exists", edge)
	}
	// Attempt to reuse link
	return fmt.Errorf("splitting an existing link is currently unsupported")
}

func (node *Node) Satisfies(other *Node) bool {
	return other.requireMask&node.provideMask == other.requireMask &&
		node.lengthsMask&other.lengthsMask > 0
}

func (node *Node) String() string {
	return fmt.Sprintf(
		"Node('%s', '%s', %.2g)",
		MaskAlphabet(node.provideMask, node.requireMask),
		LengthAlphabet(node.lengthsMask),
		node.matchWeight,
	)
}
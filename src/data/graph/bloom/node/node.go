package node

import (
	"fmt"
	"math"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

// Graph node with bloom-filter style optimizations.
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
	// Array of outgoing Nodes (index assigned by Position from mask.go).
	Links []NodeLink
}

type NodeLink struct {
	Prefix string
	Node   *Node
}

func NewNode(matchWeight ...weight.Weight) *Node {
	result := Node{}
	result.RequireMask = mask.UNSET
	if len(matchWeight) == 1 {
		result.Match(matchWeight[0])
	}
	return &result
}

func (node *Node) Match(weight weight.Weight) {
	if node.MatchWeight != 0.0 {
		panic(fmt.Errorf("duplicate attempts to set match weight (%f and %f)",
			node.MatchWeight, weight))
	}
	node.MatchWeight = weight
	node.LengthsMask |= 0b1 // Match at current position
	node.Weight(weight)
}

func (node *Node) Weight(weight weight.Weight) {
	node.MaxWeight = math.Max(node.MaxWeight, weight)
}

func (node *Node) Link(path string, child *Node) error {
	if len(path) == 0 {
		return fmt.Errorf("attempted to link empty key")
	}
	runes := []rune(path)
	edgeMask := mask.Mask(0)
	for _, c := range runes {
		mask, err := mask.AlphabetMask(c)
		if err != nil {
			return fmt.Errorf("error while linking: %w", err)
		}
		edgeMask |= mask
	}
	// Inherit maxWeight.
	node.Weight(child.MaxWeight)
	// Provide anything ANY children provides (including the edge itself).
	node.ProvideMask |= edgeMask | mask.Mask(child.ProvideMask)
	if child.RequireMask == mask.UNSET {
		// Ignore the child's require mask if it is UNSET.
		node.RequireMask &= edgeMask
	} else {
		// Require anything ALL children requires (including the edge itself).
		node.RequireMask &= edgeMask | mask.Mask(child.RequireMask)
	}
	// Inherit matching lengths.
	node.LengthsMask |= child.LengthsMask << len(runes)
	link := NodeLink{
		path,
		child,
	}
	// Optimized path for first link.
	if node.Links == nil {
		node.Links = []NodeLink{
			link,
		}
		return nil
	}
	// append(...) will ensure there is room for all (old+new) links.
	node.Links = append(node.Links, link)
	// Scan links to validate they are in sorted order and there are no duplicates.
	links := node.Links
	for second := len(links) - 1; second > 0; second-- {
		first := second - 1
		if links[first].Prefix[0] == links[second].Prefix[0] {
			if node.Links[first].Prefix == links[second].Prefix {
				// Proposed link already exists.
				return fmt.Errorf("link '%s' already exists", path)
			}
			// Attempt to reuse link.
			return fmt.Errorf("splitting an existing link is currently unsupported")
		}
		if links[second].Node.MaxWeight > links[first].Node.MaxWeight {
			// The second node is better than first; swap.
			links[first], links[second] = links[second], links[first]
		}
	}
	return nil
}

func (node *Node) Satisfies(other *Node) bool {
	return other.RequireMask&node.ProvideMask == other.RequireMask &&
		node.LengthsMask&other.LengthsMask > 0
}

func (node *Node) String() string {
	return fmt.Sprintf(
		"Node('%s', '%s', %.2g)",
		mask.MaskAlphabet(node.ProvideMask, node.RequireMask),
		mask.LengthAlphabet(node.LengthsMask),
		node.MatchWeight,
	)
}

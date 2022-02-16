package node

import (
	"fmt"
	"math"
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

func NewNode(matchWeight ...weight.Weight) *Node {
	result := &Node{
		RequireMask: mask.UNSET,
	}
	if len(matchWeight) == 1 {
		result.Match(matchWeight[0])
	}
	return result
}

func (node *Node) Matches() bool {
	return node.LengthsMask&mask.Mask(0b1) == 1
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

func (node *Node) MaskPath(path string) error {
	edgeMask, runeLength, err := mask.EdgeMaskAndLength(path)
	if err != nil {
		return err
	}
	// Provide anything the edge provides.
	node.ProvideMask |= edgeMask
	// Require anything the edge provides.
	node.RequireMask &= edgeMask
	// Set match at the end of path.
	node.LengthsMask |= 1 << runeLength
	return nil
}

func (node *Node) MaskPathToChild(path string, child *Node) error {
	// Inherit maxWeight.
	node.Weight(child.MaxWeight)
	if path == "" {
		// Optimized path for zero-length paths.
		node.Union(child)
	} else {
		edgeMask, runeLength, err := mask.EdgeMaskAndLength(path)
		if err != nil {
			return err
		}
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
		node.LengthsMask |= child.LengthsMask << runeLength
	}
	return nil
}

func (node *Node) Intersection(other *Node) *Node {
	// Copy weights using MIN operation.
	node.MatchWeight = math.Min(node.MatchWeight, other.MatchWeight)
	node.MaxWeight = math.Min(node.MaxWeight, other.MaxWeight)
	node.ProvideMask &= other.ProvideMask // Only provide what everyone can.
	// Require whatever anyone requires.
	node.RequireMask |= other.RequireMask
	if node.RequireMask == mask.UNSET {
		// Exit blocked; only keep lowest bit on LengthsMask.
		node.LengthsMask &= other.LengthsMask & mask.Mask(0b1)
	} else if node.RequireMask == node.RequireMask&node.ProvideMask {
		// Only consider aligned matches.
		node.LengthsMask &= other.LengthsMask
	} else {
		// Unsatisfiable requirements
		node.LengthsMask = mask.Mask(0)
	}
	return node
}

func (node *Node) Union(other *Node) *Node {
	// Copy weights using MAX operation.
	node.MatchWeight = math.Max(node.MatchWeight, other.MatchWeight)
	node.MaxWeight = math.Max(node.MaxWeight, other.MaxWeight)
	node.ProvideMask |= other.ProvideMask // Provide anything anyone can.
	node.RequireMask &= other.RequireMask // Only require whatever everyone requires.
	node.LengthsMask |= other.LengthsMask // Consider either matches.
	return node
}

func (node *Node) Weight(weight weight.Weight) {
	node.MaxWeight = math.Max(node.MaxWeight, weight)
}

func (node *Node) String() string {
	return Format("Node", node)
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

package node

import (
	"fmt"
	"math"
	"regexp"
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

type NodeMetadataProvider interface {
	Metadata(path string) []weight.WeightedString
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

func (node *Node) Copy() *Node {
	return &Node{
		MatchWeight: node.MatchWeight,
		MaxWeight:   node.MaxWeight,
		ProvideMask: node.ProvideMask,
		RequireMask: node.RequireMask,
		LengthsMask: node.LengthsMask,
	}
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

func (node *Node) MaskEdgeMask(edgeMask mask.Mask) {
	// Provide anything the edge provides.
	node.ProvideMask |= edgeMask
	// Require anything the edge provides.
	node.RequireMask &= edgeMask
}

func (node *Node) MaskEdgeMaskToChild(edgeMask mask.Mask, child *Node) {
	oneBitRemoved := edgeMask & (edgeMask - 1)
	if oneBitRemoved == 0 {
		// The path to child has only one option which implies path is required.
		node.maskMaskDistanceToChild(edgeMask, 1, child)
	} else {
		// Inherit requirements from child.
		node.MaskDistanceToChild(1, child)
		node.ProvideMask |= edgeMask
		// If node's RequireMask is still unset...
		if node.RequireMask == mask.UNSET {
			// Clear it because multiple runes implies path to child is not required.
			node.RequireMask = mask.Mask(0)
		}
	}
}

func (node *Node) MaskPath(path string) error {
	edgeMask, runeLength, err := mask.EdgeMaskAndLength(path)
	if err != nil {
		return err
	}
	node.MaskEdgeMask(edgeMask)
	// Set match at the end of path.
	node.LengthsMask |= 1 << runeLength
	return nil
}

func (node *Node) MaskDistanceToChild(distance int, child *Node) {
	// Inherit maxWeight.
	node.Weight(child.MaxWeight)
	if distance == 0 {
		// Optimized path for zero-length paths.
		node.Union(child)
	} else {
		// Provide anything ANY children provides.
		node.ProvideMask |= mask.Mask(child.ProvideMask)
		// Inherit matching lengths.
		node.LengthsMask |= mask.ShiftLength(child.LengthsMask, distance)
		if child.RequireMask == mask.UNSET {
			// Ignore the child's require mask if it is UNSET.
		} else if child.Matches() {
			// Since the child is a match no requirements are inherited.
		} else {
			// Require anything ALL children requires.
			node.RequireMask &= mask.Mask(child.RequireMask)
		}
	}
}

func (node *Node) MaskPathToChild(path string, child *Node) error {
	edgeMask, runeLength, err := mask.EdgeMaskAndLength(path)
	if err != nil {
		return err
	}
	return node.maskMaskDistanceToChild(edgeMask, runeLength, child)
}

func (node *Node) maskMaskDistanceToChild(edgeMask mask.Mask, distance int, child *Node) error {
	// Inherit maxWeight.
	node.Weight(child.MaxWeight)
	if distance == 0 {
		// Optimized path for zero-length paths.
		node.Union(child)
	} else {
		// Provide anything ANY children provides (including the edge itself).
		node.ProvideMask |= edgeMask | child.ProvideMask
		// Inherit matching lengths.
		node.LengthsMask |= mask.ShiftLength(child.LengthsMask, distance)
		if child.RequireMask == mask.UNSET {
			// Ignore the child's require mask if it is UNSET.
			node.RequireMask &= edgeMask
		} else if child.Matches() {
			// Since the child is a match only the edge is required.
			node.RequireMask &= edgeMask
		} else {
			// Require anything ALL children requires (including the edge itself).
			node.RequireMask &= edgeMask | child.RequireMask
		}
	}
	return nil
}

func (node *Node) RepeatLengthMask(interval int) {
	node.LengthsMask = mask.RepeatLengths(node.LengthsMask, interval)
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

var lengthMaskRemover = regexp.MustCompile(" [◌●]+·*")

func Format(name string, node *Node) string {
	parts := []string{}
	if node.Matches() {
		parts = append(parts, weight.String(node.MatchWeight))
	}
	acc := mask.MaskString(node.ProvideMask, node.RequireMask)
	if len(acc) > 0 {
		parts = append(parts, acc)
	}
	acc = mask.LengthString(node.LengthsMask)
	if len(acc) > 0 {
		parts = append(parts, acc)
	}
	acc = strings.Join(parts, " ")
	if len(acc) > 0 {
		return name + ": " + acc
	}
	return name
}

func StringChildren(iterator NodeIterator, depth ...int) string {
	if len(depth) > 0 {
		return stringChildrenWithPrefix(iterator, "", depth[0])
	}
	return stringChildrenWithPrefix(iterator, "", 1)
}

func stringChildrenWithPrefix(iterator NodeIterator, base string, remaining int) string {
	nodeString := lengthMaskRemover.ReplaceAllLiteralString(iterator.String(), "")
	if remaining == 0 {
		return nodeString
	}
	results := []string{
		nodeString,
	}
	if iterator.Root().LengthsMask > 1 {
		results = append(results, base+"│"+mask.LengthString(iterator.Root().LengthsMask))
	}
	items := iterator.Items(NodeAcceptAll)
	for items.HasNext() {
		path, item := items.Next()
		line := "├"
		prefix := "│"
		if !items.HasNext() {
			line = "└"
			if base == "" {
				prefix = "·"
			} else {
				prefix = " "
			}
		}
		prefix += strings.Repeat(" ", len(path)-1)
		matchString := " "
		if item.Root().Matches() {
			matchString = "●"
		}
		results = append(results, fmt.Sprintf("%s%s%s->%s",
			base+line, path, matchString, stringChildrenWithPrefix(item, base+prefix, remaining-1)))

	}
	return strings.Join(results, "\n")
}

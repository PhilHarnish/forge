package trie

import (
	"fmt"
	"math"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

// Trie with bloom-filter style optimizations.
type Trie struct {
	node.Node
	links []trieLink
}

type trieLink struct {
	Prefix string
	Node   *Trie
}

func NewTrie(matchWeight ...weight.Weight) *Trie {
	result := Trie{}
	result.RequireMask = mask.UNSET
	if len(matchWeight) == 1 {
		result.Match(matchWeight[0])
	}
	return &result
}

func (trie *Trie) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return newIteratorItems(acceptor, trie)
}

func (trie *Trie) Match(weight weight.Weight) {
	if trie.MatchWeight != 0.0 {
		panic(fmt.Errorf("duplicate attempts to set match weight (%f and %f)",
			trie.MatchWeight, weight))
	}
	trie.MatchWeight = weight
	trie.LengthsMask |= 0b1 // Match at current position
	trie.Weight(weight)
}

func (trie *Trie) Weight(weight weight.Weight) {
	trie.MaxWeight = math.Max(trie.MaxWeight, weight)
}

func (trie *Trie) Link(path string, child *Trie) error {
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
	trie.Weight(child.MaxWeight)
	// Provide anything ANY children provides (including the edge itself).
	trie.ProvideMask |= edgeMask | mask.Mask(child.ProvideMask)
	if child.RequireMask == mask.UNSET {
		// Ignore the child's require mask if it is UNSET.
		trie.RequireMask &= edgeMask
	} else {
		// Require anything ALL children requires (including the edge itself).
		trie.RequireMask &= edgeMask | mask.Mask(child.RequireMask)
	}
	// Inherit matching lengths.
	trie.LengthsMask |= child.LengthsMask << len(runes)
	link := trieLink{
		path,
		child,
	}
	// Optimized path for first link.
	if trie.links == nil {
		trie.links = []trieLink{
			link,
		}
		return nil
	}
	// append(...) will ensure there is room for all (old+new) links.
	trie.links = append(trie.links, link)
	// Scan links to validate they are in sorted order and there are no duplicates.
	links := trie.links
	for second := len(links) - 1; second > 0; second-- {
		first := second - 1
		if links[first].Prefix[0] == links[second].Prefix[0] {
			if trie.links[first].Prefix == links[second].Prefix {
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

func (trie *Trie) Satisfies(other *Trie) bool {
	return other.RequireMask&trie.ProvideMask == other.RequireMask &&
		trie.LengthsMask&other.LengthsMask > 0
}

func (trie *Trie) String() string {
	return node.Format("Trie", &trie.Node)
}

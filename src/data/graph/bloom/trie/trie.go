package trie

import (
	"fmt"
	"strings"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

// Trie with bloom-filter style optimizations.
type Trie struct {
	*node.Node
	links []trieLink
}

type trieLink struct {
	prefix string
	node   *Trie
}

func NewTrie(matchWeight ...weight.Weight) *Trie {
	return &Trie{
		Node:  node.NewNode(matchWeight...),
		links: nil,
	}
}

func (trie *Trie) Root() *node.Node {
	return trie.Node
}

func (trie *Trie) Items(generator node.NodeGenerator) node.NodeItems {
	return newTrieItems(generator, trie)
}

func (trie *Trie) Link(path string, child *Trie) error {
	if len(path) == 0 {
		return fmt.Errorf("attempted to link empty key")
	}
	err := trie.Node.MaskPathToChild(path, child.Node)
	if err != nil {
		return fmt.Errorf("error while linking: %w", err)
	}
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
		if links[first].prefix[0] == links[second].prefix[0] {
			if trie.links[first].prefix == links[second].prefix {
				// Proposed link already exists.
				return fmt.Errorf("link '%s' already exists", path)
			}
			// Attempt to reuse link.
			panic("splitting an existing link is currently unsupported")
		}
		if links[second].node.MaxWeight > links[first].node.MaxWeight {
			// The second node is better than first; swap.
			links[first], links[second] = links[second], links[first]
		}
	}
	return nil
}

func (trie *Trie) Get(path string) *Trie {
	child, remaining := trie.seek(path, nil)
	if remaining == "" {
		return child
	}
	return nil
}

func (trie *Trie) Add(path string, matchWeight weight.Weight) error {
	runes := []rune(path)
	edgeMasks, err := mask.AlphabetMasks(runes)
	if err != nil {
		return err
	}
	if len(edgeMasks) != len(path) {
		return fmt.Errorf("unicode paths are unsupported")
	}
	parent, remaining := trie.seek(path, edgeMasks)
	if remaining == "" {
		return fmt.Errorf("node %s already exists at '%s'", parent.String(), path)
	}
	return parent.Link(remaining, NewTrie(matchWeight))
}

func (trie *Trie) seek(path string, provideMasks []mask.Mask) (child *Trie, remaining string) {
	for _, link := range trie.links {
		if path == link.prefix {
			return link.node, ""
		} else if strings.HasPrefix(path, link.prefix) {
			remainingPath := path[len(link.prefix):]
			if provideMasks != nil {
				trie.Node.LengthsMask |= mask.Mask(1 << len(provideMasks))
				for i := range link.prefix {
					trie.Node.ProvideMask |= provideMasks[i]
				}
				provideMasks = provideMasks[len(link.prefix):]
			}
			return link.node.seek(remainingPath, provideMasks)
		}
	}
	return trie, path
}

func (trie *Trie) String() string {
	return node.Format("Trie", trie.Node)
}

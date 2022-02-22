package retrie

import (
	"unicode"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
)

type reTrieNode struct {
	rootNode *node.Node
	links    []*reTrieLink
}

type reTrieLink struct {
	prefix string
	runes  []rune
	node   node.NodeIterator
}

func newReTrieNode(root *node.Node) *reTrieNode {
	return &reTrieNode{
		rootNode: root,
		links:    []*reTrieLink{},
	}
}

func (root *reTrieNode) Copy() *reTrieNode {
	result := &reTrieNode{
		rootNode: root.rootNode.Copy(),
		links:    make([]*reTrieLink, len(root.links)),
	}
	copy(result.links, root.links)
	return result
}

func (root *reTrieNode) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return newTrieItems(acceptor, root)
}

func (root *reTrieNode) Root() *node.Node {
	return root.rootNode
}

func (root *reTrieNode) String() string {
	return node.Format("ReTrie", root.Root())
}

func (root *reTrieNode) linkAnyChar(child *reTrieNode, repeats bool) {
	root.rootNode.ProvideMask = mask.ALL
	root.rootNode.MaskDistanceToChild(1, child.rootNode)
	if repeats {
		root.rootNode.RepeatLengthMask(1)
	}
	root.addLink(&reTrieLink{
		prefix: DOT_PREFIX,
		node:   child,
	})
}

func (root *reTrieNode) linkPath(path string, child *reTrieNode, repeats bool) {
	root.rootNode.MaskPathToChild(path, child.rootNode)
	if repeats {
		root.rootNode.RepeatLengthMask(len(path))
	}
	root.addLink(&reTrieLink{
		prefix: path,
		node:   child,
	})
}

func (root *reTrieNode) linkRunes(runes []rune, child *reTrieNode, repeats bool) {
	if len(runes)%2 != 0 {
		panic("linkRunes does not support an odd number of runes")
	}
	pathMask := mask.Mask(0b0)
	i := 0
	filteredRunes := make([]rune, 0, len(runes))
	for i < len(runes) {
		start := runes[i]
		end := runes[i+1]
		rangeMask, err := mask.AlphabetMaskRange(start, end)
		if err == nil {
			pathMask |= rangeMask
			filteredRunes = append(filteredRunes, runes[i])
			filteredRunes = append(filteredRunes, runes[i+1])
		} else if unicode.IsLetter(start) && unicode.IsLetter(end) {
			// A letter is a reasonable character to attempt; skip.
		} else if unicode.IsNumber(start) && unicode.IsNumber(end) {
			// A number is a reasonable character to attempt; skip.
		} else if start == '_' && end == '_' {
			// _ is a reasonable character to attempt; skip.
		} else {
			panic(err)
		}
		i += 2
	}
	root.rootNode.MaskDistanceToChild(1, child.rootNode)
	if repeats {
		root.rootNode.RepeatLengthMask(1)
	}
	root.rootNode.ProvideMask |= pathMask
	root.addLink(&reTrieLink{
		runes: filteredRunes,
		node:  child,
	})
}

func (root *reTrieNode) addLink(link *reTrieLink) {
	root.links = append(root.links, link)
}

func (root *reTrieNode) optionalPath(child *reTrieNode) *reTrieNode {
	optionalLink := root.optionalLink()
	var parent node.NodeIterator = root
	if optionalLink != nil {
		parent = optionalLink.node
	}
	merged := op.Or(parent, child)
	result := root
	if optionalLink == nil {
		result = &reTrieNode{
			links: []*reTrieLink{
				{
					prefix: OPTIONAL_PREFIX,
					node:   merged,
				},
			},
		}
	} else {
		// Root already has an optional path.
		optionalLink.node = merged
	}
	result.rootNode = merged.Root()
	return result
}

func (root *reTrieNode) optionalLink() *reTrieLink {
	if len(root.links) == 1 && root.links[0].prefix == OPTIONAL_PREFIX {
		return root.links[0]
	}
	return nil
}

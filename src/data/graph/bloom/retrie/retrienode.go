package retrie

import (
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type reTrieNode struct {
	rootNode *node.Node
	links    []*reTrieLink
}

type reTrieLink struct {
	prefix string
	runes  []rune
	node   *reTrieNode
}

func newReTrieNode(root *node.Node) *reTrieNode {
	return &reTrieNode{
		rootNode: root,
		links:    []*reTrieLink{},
	}
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

func (root *reTrieNode) linkRune(path string, child *reTrieNode) {
	root.rootNode.MaskPathToChild(path, child.rootNode)
	root.links = append(root.links, &reTrieLink{
		prefix: path,
		node:   child,
	})
}

func (root *reTrieNode) linkRunes(runes []rune, child *reTrieNode) {
	if len(runes)%2 != 0 {
		panic("linkRunes does not support an odd number of runes")
	}
	pathMask := mask.Mask(0b0)
	i := 0
	for i < len(runes) {
		rangeMask, err := mask.AlphabetMaskRange(runes[i], runes[i+1])
		if err != nil {
			panic(err)
		}
		pathMask |= rangeMask
		i += 2
	}
	root.rootNode.MaskDistanceToChild(1, child.rootNode)
	root.rootNode.ProvideMask |= pathMask
	root.links = append(root.links, &reTrieLink{
		runes: runes,
		node:  child,
	})
}

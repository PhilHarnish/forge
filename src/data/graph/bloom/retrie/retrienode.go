package retrie

import "github.com/philharnish/forge/src/data/graph/bloom/node"

type reTrieNode struct {
	rootNode *node.Node
	links    []*reTrieLink
}

type reTrieLink struct {
	prefix string
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

func (root *reTrieNode) linkRunes(runes []rune, child *reTrieNode) {
	path := string(runes)
	root.rootNode.MaskPathToChild(path, child.rootNode)
	root.links = append(root.links, &reTrieLink{
		prefix: path,
		node:   child,
	})
}

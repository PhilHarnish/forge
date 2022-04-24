package retrie

import (
	"regexp/syntax"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type reTrieAnagramNode struct {
	// TODO: Cache results.
	// table     map[dfaId]*reTrieNode
	options   []*syntax.Regexp
	rootNodes []*node.Node
	rootNode  *node.Node
	remaining dfaId
	parent    *reTrieNode
	child     *reTrieNode
	repeats   bool
}

func newReTrieAnagramNodeChild(options []*syntax.Regexp, rootNodes []*node.Node,
	remaining dfaId, child *reTrieNode, repeats bool) *reTrieAnagramNode {
	return &reTrieAnagramNode{
		// TODO: Cache results.
		// table:     map[dfaId]*reTrieNode{},
		options:   options,
		rootNodes: rootNodes,
		remaining: remaining,
		child:     child,
		repeats:   repeats,
	}
}

// TODO: Initialize all at once.
// func newReTrieAnagramNode(directory *reTrieDirectory, options []*syntax.Regexp,
// 	child *reTrieNode, repeats bool) *reTrieAnagramNode {
// 	table := precomputeAnagramTable(directory, options, child, repeats)
// 	rootNodes := precomputeAnagramNodes(options, child, repeats)
// 	remaining := (dfaId(1) << len(options)) - 1
// 	return &reTrieAnagramNode{
// 		table:     table,
// 		options:   options,
// 		rootNodes: rootNodes,
// 		remaining: remaining,
// 		child:     child,
// 		repeats:   repeats,
// 	}
// }

func (root *reTrieAnagramNode) Items(acceptor node.NodeAcceptor) node.NodeItems {
	root.expandParent()
	return root.parent.Items(acceptor)
}

func (root *reTrieAnagramNode) Root() *node.Node {
	if root.rootNode == nil {
		root.rootNode = root.child.Root().Copy()
		for i, rootNode := range root.rootNodes {
			optionId := dfaId(1) << i
			if (root.remaining & optionId) == 0 {
				continue
			} else {
				root.rootNode.MaskConcatenateChild(rootNode)
			}
		}
	}
	return root.rootNode
}

func (root *reTrieAnagramNode) String() string {
	return node.Format("ReTrieAnagram", root.Root())
}

func (root *reTrieAnagramNode) expandParent() {
	if root.parent != nil {
		return
	}
	// TODO: Cache results.
	// result, exists := root.table[root.remaining]
	// if exists {
	// 	root.parent = result
	// 	return
	// }
	tempDirectory := newDfaDirectory()
	root.parent = tempDirectory.addNode(node.NewNode())
	root.parent = expandAnagram(tempDirectory, root.options, root.rootNodes, root.remaining,
		root.parent, root.child, root.repeats)
	// TODO: Cache results.
	// root.table[root.remaining] = root.parent
}

// TODO: Precompute.
// func precomputeAnagramTable(directory *reTrieDirectory, options []*syntax.Regexp, child *reTrieNode, repeats bool) map[dfaId]*reTrieNode {
// 	result := map[dfaId]*reTrieNode{}
// 	for i, option := range options {
// 		optionId := dfaId(1) << i
// 		result[optionId] = directory.linker(nil, child, option, repeats)
// 	}
// 	return result
// }

func precomputeAnagramNodes(options []*syntax.Regexp, child *reTrieNode, repeats bool) []*node.Node {
	tempDirectory := newDfaDirectory()
	result := make([]*node.Node, len(options))
	exit := tempDirectory.addNode(node.NewNode(child.rootNode.MaxWeight))
	for i, option := range options {
		tempParent := tempDirectory.linker(nil, exit, option, repeats)
		result[i] = tempParent.rootNode
	}
	return result
}

func expandAnagram(directory *reTrieDirectory, options []*syntax.Regexp, rootNodes []*node.Node, parentRemaining dfaId,
	parent *reTrieNode, child *reTrieNode, repeats bool) *reTrieNode {
	for i, option := range options {
		optionId := dfaId(1) << i
		if (parentRemaining & optionId) == 0 {
			continue
		}
		childRemaining := parentRemaining - optionId
		if childRemaining == 0 {
			return directory.linker(parent, child, option, repeats)
		}
		embeddedNode := newReTrieAnagramNodeChild(options, rootNodes, childRemaining, child, repeats)
		out := newEmbeddedReTrieNode(embeddedNode)
		parent = directory.linker(parent, out, option, repeats)
	}
	return parent
}

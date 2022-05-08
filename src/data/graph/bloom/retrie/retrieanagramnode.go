package retrie

import (
	"regexp/syntax"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type reTrieAnagramBase struct {
	directory *reTrieDirectory
	options   []*syntax.Regexp
	rootNodes []*node.Node
	offset    dfaId
	child     *reTrieNode
	repeats   bool
}

type reTrieAnagramNode struct {
	*reTrieAnagramBase
	rootNode  *node.Node
	remaining dfaId
}

func newReTrieAnagramNodeChild(parent *reTrieAnagramNode, remaining dfaId) *reTrieAnagramNode {
	return &reTrieAnagramNode{
		reTrieAnagramBase: parent.reTrieAnagramBase,
		remaining:         remaining,
	}
}

func newReTrieAnagramNodeParent(root *reTrieNode, options []*syntax.Regexp, child *reTrieNode, repeats bool) *reTrieNode {
	parentAnagramNode := newReTrieAnagramNode(root.directory, options, child, repeats)
	return parentAnagramNode.expandAnagram(root)
}

func newReTrieAnagramNode(directory *reTrieDirectory, options []*syntax.Regexp,
	child *reTrieNode, repeats bool) *reTrieAnagramNode {
	remaining, offset := precomputeAnagramTable(directory, options, child, repeats)
	rootNodes := precomputeAnagramNodes(options, child, repeats)
	return &reTrieAnagramNode{
		reTrieAnagramBase: &reTrieAnagramBase{
			directory: directory,
			options:   options,
			rootNodes: rootNodes,
			offset:    offset,
			child:     child,
			repeats:   repeats,
		},
		remaining: remaining,
	}
}

func (root *reTrieAnagramNode) Items(generator node.NodeGenerator) node.NodeItems {
	return root.directory.get(root.remaining, root.getParent).Items(generator)
}

func (root *reTrieAnagramNode) Root() *node.Node {
	if root.rootNode == nil {
		root.rootNode = root.child.Root().Copy()
		remaining := root.remaining
		for i, rootNode := range root.rootNodes {
			optionId := dfaId(1) << (root.offset + dfaId(i))
			if (remaining & optionId) == 0 {
				continue
			}
			root.rootNode.MaskPrependChild(rootNode)
			remaining -= optionId
			if remaining == 0 {
				break
			}
		}
	}
	return root.rootNode
}

func (root *reTrieAnagramNode) String() string {
	return node.Format("ReTrieAnagram", root.Root())
}

func (root *reTrieAnagramNode) getParent() *reTrieNode {
	return root.expandAnagram(nil)
}

func (root *reTrieAnagramNode) expandAnagram(parent *reTrieNode) *reTrieNode {
	for i, option := range root.options {
		optionId := dfaId(1) << (root.offset + dfaId(i))
		if (root.remaining & optionId) == 0 {
			continue
		}
		childRemaining := root.remaining - optionId
		embeddedNode := newReTrieAnagramNodeChild(root, childRemaining)
		out := newEmbeddedReTrieNode(embeddedNode)
		parent = root.directory.linker(parent, out, option, root.repeats)
	}
	return parent
}

func precomputeAnagramTable(directory *reTrieDirectory, options []*syntax.Regexp, child *reTrieNode, repeats bool) (remaining dfaId, offset dfaId) {
	offset = directory.next
	parents := make([]*reTrieNode, len(options))
	for i := range options {
		parent := directory.addNode(node.NewNode())
		parents[i] = parent
		remaining |= parent.id
	}
	for i, option := range options {
		// Add each exit path to directory. These will be used on exit.
		directory.linker(parents[i], child, option, repeats)
	}
	return remaining, offset
}

func precomputeAnagramNodes(options []*syntax.Regexp, child *reTrieNode, repeats bool) []*node.Node {
	var tempDirectory *reTrieDirectory
	result := make([]*node.Node, len(options))
	exit := tempDirectory.addNode(node.NewNode(child.Root().MaxWeight))
	for i, option := range options {
		tempParent := tempDirectory.linker(nil, exit, option, repeats)
		result[i] = tempParent.Root()
	}
	return result
}

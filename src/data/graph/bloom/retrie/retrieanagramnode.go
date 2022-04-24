package retrie

import (
	"fmt"
	"regexp/syntax"
	"strconv"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type reTrieAnagramNode struct {
	directory *reTrieDirectory
	options   []*syntax.Regexp
	rootNodes []*node.Node
	rootNode  *node.Node
	remaining dfaId
	offset    dfaId
	parent    *reTrieNode
	child     *reTrieNode
	repeats   bool
}

func newReTrieAnagramNodeChild(parent *reTrieAnagramNode, remaining dfaId) *reTrieAnagramNode {
	return &reTrieAnagramNode{
		directory: parent.directory,
		options:   parent.options,
		rootNodes: parent.rootNodes,
		remaining: remaining,
		offset:    parent.offset,
		child:     parent.child,
		repeats:   parent.repeats,
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
	fmt.Println("Anagram node created with remaining =", strconv.FormatUint(remaining, 2))
	return &reTrieAnagramNode{
		directory: directory,
		options:   options,
		rootNodes: rootNodes,
		remaining: remaining,
		offset:    offset,
		child:     child,
		repeats:   repeats,
	}
}

func (root *reTrieAnagramNode) Items(acceptor node.NodeAcceptor) node.NodeItems {
	root.expandParent()
	return root.parent.Items(acceptor)
}

func (root *reTrieAnagramNode) Root() *node.Node {
	if root.rootNode == nil {
		root.rootNode = root.child.Root().Copy()
		for i, rootNode := range root.rootNodes {
			optionId := dfaId(1) << (root.offset + dfaId(i))
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
	indexed, found := root.directory.table[root.remaining]
	if found {
		root.parent = indexed
		return
	}
	root.parent = root.expandAnagram(nil)
}

func (root *reTrieAnagramNode) expandAnagram(parent *reTrieNode) *reTrieNode {
	for i, option := range root.options {
		optionId := dfaId(1) << (root.offset + dfaId(i))
		if (root.remaining & optionId) == 0 {
			continue
		}
		childRemaining := root.remaining - optionId
		if childRemaining == 0 {
			return root.directory.linker(parent, root.child, option, root.repeats)
		}
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
		directory.linker(parents[i], child, option, repeats)
		fmt.Println("Indexing", parents[i].id, "which is", option.String(), "to", parents[i].String())
	}
	return remaining, offset
}

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

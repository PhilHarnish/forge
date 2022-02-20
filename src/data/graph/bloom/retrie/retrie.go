package retrie

import (
	"fmt"
	"regexp/syntax"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type reTrie struct {
	rootTrieNode *reTrieNode
	captureCount int
	captureNames []string
}

func NewReTrie(regularExpression string, matchWeight weight.Weight) *reTrie {
	re, err := syntax.Parse(regularExpression, syntax.Perl)
	if err != nil {
		panic(err)
	}
	captureCount := re.MaxCap()
	captureNames := re.CapNames()

	re = re.Simplify()
	return &reTrie{
		rootTrieNode: linker(newReTrieNode(node.NewNode(matchWeight)), re),
		captureCount: captureCount,
		captureNames: captureNames,
	}
}

func (root *reTrie) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return root.rootTrieNode.Items(acceptor)
}

func (root *reTrie) Root() *node.Node {
	return root.rootTrieNode.Root()
}

func (root *reTrie) String() string {
	return root.rootTrieNode.String()
}

func linker(root *reTrieNode, re *syntax.Regexp) *reTrieNode {
	switch re.Op {
	case syntax.OpAnyChar, syntax.OpAnyCharNotNL:
		parent := newReTrieNode(node.NewNode())
		parent.linkAnyChar(root)
		return parent
	case syntax.OpEmptyMatch:
		return root
	case syntax.OpCharClass: // [xyz]
		parent := newReTrieNode(node.NewNode())
		parent.linkRunes(re.Rune, root)
		return parent
	case syntax.OpConcat: // xyz
		i := len(re.Sub)
		for i > 0 {
			i--
			root = linker(root, re.Sub[i])
		}
		return root
	case syntax.OpLiteral: // x
		parent := newReTrieNode(node.NewNode())
		parent.linkPath(string(re.Rune), root)
		return parent
	case syntax.OpQuest: // x?
		if len(re.Sub) != 1 {
			panic("Unable to handle OpQuest with 2+ Sub options")
		}
		// Offer link to alternate path.
		parent := linker(root, re.Sub[0])
		// The alternate path is optional so copy this node's information.
		parent.rootNode.Union(root.rootNode)
		return parent
	}
	panic(fmt.Sprintf("Unsupported instruction: %d", re.Op))
}

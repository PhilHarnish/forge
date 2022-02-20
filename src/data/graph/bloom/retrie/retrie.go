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
	case syntax.OpEmptyMatch:
		return root
	case syntax.OpCharClass:
		parent := newReTrieNode(node.NewNode())
		parent.linkRunes(re.Rune, root)
		return parent
	case syntax.OpConcat:
		i := len(re.Sub)
		for i > 0 {
			i--
			root = linker(root, re.Sub[i])
		}
		return root
	case syntax.OpLiteral:
		parent := newReTrieNode(node.NewNode())
		parent.linkPath(string(re.Rune), root)
		return parent
	}
	panic(fmt.Sprintf("Unsupported instruction: %d", re.Op))
}

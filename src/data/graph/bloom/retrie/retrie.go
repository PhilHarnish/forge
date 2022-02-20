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
		rootTrieNode: linker(nil, newReTrieNode(node.NewNode(matchWeight)), re, false),
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

func ensureNode(given *reTrieNode) *reTrieNode {
	if given == nil {
		return newReTrieNode(node.NewNode())
	}
	return given
}

func linker(parent *reTrieNode, child *reTrieNode, re *syntax.Regexp, repeats bool) *reTrieNode {
	switch re.Op {
	case syntax.OpAlternate:
		parent = ensureNode(parent)
		for _, alternative := range re.Sub {
			parent = linker(parent, child, alternative, repeats)
		}
		return parent
	case syntax.OpAnyChar, syntax.OpAnyCharNotNL:
		parent = ensureNode(parent)
		parent.linkAnyChar(child, repeats)
		return parent
	case syntax.OpBeginLine, syntax.OpEndLine, syntax.OpBeginText, syntax.OpEndText:
		if parent != nil {
			panic(fmt.Sprintf("Cannot connect parent -> child with instruction: %d", re.Op))
		}
		return child
	case syntax.OpEmptyMatch:
		if parent != nil {
			panic(fmt.Sprintf("Cannot connect parent -> child with instruction: %d", re.Op))
		}
		return child
	case syntax.OpCharClass: // [xyz]
		parent = ensureNode(parent)
		parent.linkRunes(re.Rune, child, repeats)
		return parent
	case syntax.OpConcat: // xyz
		i := len(re.Sub)
		for i > 0 {
			i--
			parent, child = nil, linker(parent, child, re.Sub[i], repeats)
		}
		return child
	case syntax.OpLiteral: // x
		parent = ensureNode(parent)
		parent.linkPath(string(re.Rune), child, repeats)
		return parent
	case syntax.OpPlus:
		if len(re.Sub) != 1 {
			panic("Unable to handle OpPlus with 2+ Sub options")
		}
		parent = linker(parent, child, re.Sub[0], true)
		// However, child may optionally link through as well.
		linker(child, child, re.Sub[0], true)
		return parent
	case syntax.OpQuest: // x?
		if len(re.Sub) != 1 {
			panic("Unable to handle OpQuest with 2+ Sub options")
		}
		// Offer link to alternate path.
		parent = linker(parent, child, re.Sub[0], repeats)
		// The alternate path is optional so copy this node's information.
		parent.rootNode.Union(child.rootNode)
		return parent
	}
	panic(fmt.Sprintf("Unsupported instruction: %d", re.Op))
}

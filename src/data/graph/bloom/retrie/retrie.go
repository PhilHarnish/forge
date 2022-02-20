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
	program, err := syntax.Compile(re)
	if err != nil {
		panic(err)
	}

	return &reTrie{
		rootTrieNode: linker(newReTrieNode(node.NewNode(matchWeight)), extractInstructions(program)),
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

func extractInstructions(program *syntax.Prog) []syntax.Inst {
	result := program.Inst
	start := program.Start
	cursor := program.Inst[start]
	for cursor.Op == syntax.InstNop || cursor.Op == syntax.InstCapture {
		start := cursor.Out
		cursor = program.Inst[start]
	}
	return result[start:]
}

func linker(root *reTrieNode, instructions []syntax.Inst) *reTrieNode {
	i := len(instructions)
	for i > 0 {
		i--
		instruction := instructions[i]
		switch instruction.Op {
		case syntax.InstFail, syntax.InstNop, syntax.InstMatch:
			// Do nothing.
		case syntax.InstRune:
			parent := newReTrieNode(node.NewNode())
			parent.linkRunes(instruction.Rune, root)
			root = parent
		case syntax.InstRune1:
			parent := newReTrieNode(node.NewNode())
			parent.linkRune(string(instruction.Rune), root)
			root = parent
		default:
			panic(fmt.Sprintf("Unsupported instruction: %d", instruction.Op))
		}
	}
	return root
}

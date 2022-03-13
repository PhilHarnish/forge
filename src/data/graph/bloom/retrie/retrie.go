package retrie

import (
	"fmt"
	"regexp"
	"regexp/syntax"
	"strings"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type reTrie struct {
	rootTrieNode *reTrieNode
	original     *regexp.Regexp
	captureNames []string
	instructions []*reTrieNode
	directory    *reTrieDirectory
}

type dfaId = int64

const USE_COMPILED_INSTRUCTIONS = false
const EPSILON_EXPANSION = true
const SPLIT_LITERAL_INTO_RUNES = false

var failNode = &node.Node{
	RequireMask: mask.ALL,
}
var failReTrieNode = newReTrieNode(nil, 0, failNode)

func NewReTrie(regularExpression string, matchWeight weight.Weight) *reTrie {
	re, err := syntax.Parse(regularExpression, syntax.Perl)
	if err != nil {
		panic(err)
	}
	captureNames := processCaptureNames(re.CapNames())

	re = re.Simplify()
	directory := newDfaDirectory()
	matchNode := directory.addRegexp(nil, node.NewNode(matchWeight))
	var instructions []*reTrieNode
	var rootTrieNode *reTrieNode
	if USE_COMPILED_INSTRUCTIONS {
		prog, err := syntax.Compile(re)
		if err != nil {
			panic(err)
		}
		instructions = compile(prog, matchNode)
		rootTrieNode = instructions[prog.Start]
	} else {
		rootTrieNode = directory.linker(nil, matchNode, re, false)
	}

	return &reTrie{
		rootTrieNode: rootTrieNode,
		original:     regexp.MustCompile(regularExpression),
		captureNames: captureNames,
		instructions: instructions,
		directory:    directory,
	}
}

func (root *reTrie) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return root.rootTrieNode.Items(acceptor)
}

func (root *reTrie) Root() *node.Node {
	return root.rootTrieNode.Root()
}

func (root *reTrie) Header() query.QueryRowHeader {
	return root
}

func (root *reTrie) Labels() []string {
	return root.captureNames
}

func (root *reTrie) Metadata(path string) []weight.WeightedString {
	if len(root.captureNames) == 0 {
		return nil
	}
	submatches := root.original.FindStringSubmatch(path)
	result := make([]weight.WeightedString, len(submatches)-1)
	for i, submatch := range submatches[1:] {
		result[i].String = submatch
		result[i].Weight = 1
	}
	return result
}

func (root *reTrie) String() string {
	return root.rootTrieNode.String()
}

func processCaptureNames(captureNames []string) []string {
	captureNames = captureNames[1:]
	for i, name := range captureNames {
		if name == "" {
			captureNames[i] = fmt.Sprintf("%d", i+1)
		} else {
			captureNames[i] = name
		}
	}
	return captureNames
}

func compile(program *syntax.Prog, matchNode *reTrieNode) []*reTrieNode {
	instructions := make([]*reTrieNode, len(program.Inst))
	// Initialize instructions.
	for i := range program.Inst {
		nodeAtInstruction(program, instructions, uint32(i), matchNode)
	}
	return instructions
}

func nodeAtInstruction(program *syntax.Prog, instructionNodes []*reTrieNode, index uint32, matchNode *reTrieNode) *reTrieNode {
	if instructionNodes[index] != nil {
		return instructionNodes[index]
	}
	instruction := program.Inst[index]
	// Handle terminal cases first.
	if instruction.Op == syntax.InstFail {
		instructionNodes[index] = failReTrieNode
		return failReTrieNode
	} else if instruction.Op == syntax.InstMatch {
		instructionNodes[index] = matchNode
		return matchNode
	}
	// All other instructions have an outgoing path.
	var out *reTrieNode
	if instruction.Op != syntax.InstAlt {
		// Alt's Out can produce infinite loops.
		out = nodeAtInstruction(program, instructionNodes, instruction.Out, matchNode)
	}
	var result *reTrieNode
	switch instruction.Op {
	case syntax.InstAlt:
		result = newReTrieNode(nil, 0, node.NewNode())
		arg := nodeAtInstruction(program, instructionNodes, instruction.Arg, matchNode)
		result = result.optionalPath(arg)
		instructionNodes[index] = result
		out = nodeAtInstruction(program, instructionNodes, instruction.Out, matchNode)
		result = result.optionalPath(out)
	case syntax.InstEmptyWidth:
		result = out
	case syntax.InstNop:
		result = out
	case syntax.InstRune:
		result = newReTrieNode(nil, 0, node.NewNode())
		result.linkRunes(instruction.Rune, out, false)
	case syntax.InstRune1:
		result = newReTrieNode(nil, 0, node.NewNode())
		path, exit := mergeRune1(program, index)
		out = nodeAtInstruction(program, instructionNodes, exit, matchNode)
		result.linkPath(path, out, false)
	case syntax.InstRuneAnyNotNL, syntax.InstRuneAny:
		result = newReTrieNode(nil, 0, node.NewNode())
		result.linkAnyChar(out, false)
	default:
		panic(fmt.Sprintf("Unsupported instruction: %d %v", instruction.Op, instruction))
	}
	instructionNodes[index] = result
	return result
}

func mergeRune1(program *syntax.Prog, index uint32) (string, uint32) {
	acc := &strings.Builder{}
	instruction := program.Inst[index]
	for instruction.Op == syntax.InstRune1 {
		acc.WriteRune(instruction.Rune[0])
		index = instruction.Out
		instruction = program.Inst[index]
	}
	return acc.String(), index
}

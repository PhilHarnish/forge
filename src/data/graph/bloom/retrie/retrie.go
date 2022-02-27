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
}

const USE_COMPILED_INSTRUCTIONS = false

var failNode = newReTrieNode(&node.Node{
	RequireMask: mask.ALL,
})

func NewReTrie(regularExpression string, matchWeight weight.Weight) *reTrie {
	re, err := syntax.Parse(regularExpression, syntax.Perl)
	if err != nil {
		panic(err)
	}
	captureNames := processCaptureNames(re.CapNames())

	re = re.Simplify()
	matchNode := newReTrieNode(node.NewNode(matchWeight))
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
		rootTrieNode = linker(nil, matchNode, re, false)
	}

	return &reTrie{
		rootTrieNode: rootTrieNode,
		original:     regexp.MustCompile(regularExpression),
		captureNames: captureNames,
		instructions: instructions,
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
			return parent
		}
		return child
	case syntax.OpCapture: // (xyz)
		if len(re.Sub) != 1 {
			panic("Unable to handle OpCapture with 2+ Sub options")
		}
		return linker(parent, child, re.Sub[0], repeats)
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
	case syntax.OpEmptyMatch:
		if parent == nil {
			return child
		}
		// Allow skipping straight to child.
		return parent.optionalPath(child)
	case syntax.OpLiteral: // x
		parent = ensureNode(parent)
		parent.linkPath(string(re.Rune), child, repeats)
		return parent
	case syntax.OpPlus:
		if len(re.Sub) != 1 {
			panic("Unable to handle OpPlus with 2+ Sub options")
		} else if parent == nil {
			// Only allow looping through child.
			linker(child, child, re.Sub[0], true)
			// Require at least one path through re.Sub[0]
			return linker(parent, child, re.Sub[0], true)
		}
		// We must not contaminate child which may be used by others.
		detour := child.Copy()
		// Child may optionally loop back to itself.
		linker(detour, detour, re.Sub[0], true)
		// Require at least one path through re.Sub[0]
		return linker(parent, detour, re.Sub[0], true)
	case syntax.OpQuest: // x?
		if len(re.Sub) != 1 {
			panic("Unable to handle OpQuest with 2+ Sub options")
		}
		// Offer link to alternate path.
		parent = linker(parent, child, re.Sub[0], repeats)
		// Mark the path to child as optional.
		return parent.optionalPath(child)
	case syntax.OpStar: // x*
		if len(re.Sub) != 1 {
			panic("Unable to handle OpStar with 2+ Sub options")
		} else if parent == nil {
			// Only allow looping through child.
			return linker(child, child, re.Sub[0], true)
		}
		// We must not contaminate child which may be used by others.
		detour := child.Copy()
		// Allow looping through (copied) child.
		linker(detour, detour, re.Sub[0], true)
		// Ensure it is possible to go straight from parent to child.
		return parent.optionalPath(detour)
	}
	panic(fmt.Sprintf("Unsupported instruction: %d", re.Op))
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
		instructionNodes[index] = failNode
		return failNode
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
		result = newReTrieNode(node.NewNode())
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
		result = newReTrieNode(node.NewNode())
		result.linkRunes(instruction.Rune, out, false)
	case syntax.InstRune1:
		result = newReTrieNode(node.NewNode())
		path, exit := mergeRune1(program, index)
		out = nodeAtInstruction(program, instructionNodes, exit, matchNode)
		result.linkPath(path, out, false)
	case syntax.InstRuneAnyNotNL, syntax.InstRuneAny:
		result = newReTrieNode(node.NewNode())
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

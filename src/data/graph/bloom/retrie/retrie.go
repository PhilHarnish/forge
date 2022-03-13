package retrie

import (
	"fmt"
	"regexp"
	"regexp/syntax"
	"strings"
	"unicode/utf8"

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
	directory    *dfaDirectory
}

type dfaDirectory struct {
	table     map[dfaId]*reTrieNode
	nextNfaId dfaId
	nfa2dfa   []dfaId
	nfaLinks  []*reTrieLink
}

type dfaId = int64

const USE_COMPILED_INSTRUCTIONS = false
const EPSILON_EXPANSION = true
const SPLIT_LITERAL_INTO_RUNES = false

var failNode = &node.Node{
	RequireMask: mask.ALL,
}
var failReTrieNode = newReTrieNode(nil, 0, failNode)
var anyRunes = []rune{
	'a', 'z',
	' ', ' ',
	'-', '-',
	'\'', '\'',
}

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

func newDfaDirectory() *dfaDirectory {
	result := &dfaDirectory{
		table: make(map[int64]*reTrieNode),
	}
	return result
}

func (directory *dfaDirectory) addRegexp(re *syntax.Regexp, source *node.Node) *reTrieNode {
	nfaId := directory.nextNfaId
	directory.nextNfaId++
	dfaId := dfaId(1) << nfaId
	dfaNode := newReTrieNode(directory, dfaId, source)
	directory.table[dfaId] = dfaNode
	return dfaNode
}

func (directory *dfaDirectory) addRegexpAs(re *syntax.Regexp, source *reTrieNode) *reTrieNode {
	result := directory.addRegexp(re, source.rootNode.Copy())
	return directory.merge(result, source)
}

func (directory *dfaDirectory) ensureNode(re *syntax.Regexp, given *reTrieNode) *reTrieNode {
	if given == nil {
		return directory.addRegexp(re, node.NewNode())
	}
	return given
}

func (directory *dfaDirectory) linker(parent *reTrieNode, child *reTrieNode, re *syntax.Regexp, repeats bool) *reTrieNode {
	fmt.Sprintf("DO NOT SUBMIT %s", re.String())
	switch re.Op {
	case syntax.OpAlternate:
		parent = directory.ensureNode(re, parent)
		for _, alternative := range re.Sub {
			parent = directory.linker(parent, child, alternative, repeats)
		}
		return parent
	case syntax.OpAnyChar, syntax.OpAnyCharNotNL:
		parent = directory.ensureNode(re, parent)
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
		return directory.linker(parent, child, re.Sub[0], repeats)
	case syntax.OpCharClass: // [xyz]
		parent = directory.ensureNode(re, parent)
		return parent.linkRunes(re.Rune, child, repeats)
	case syntax.OpConcat: // xyz
		i := len(re.Sub)
		for i > 0 {
			i--
			parent, child = nil, directory.linker(parent, child, re.Sub[i], repeats)
		}
		return child
	case syntax.OpEmptyMatch:
		if parent == nil {
			return child
		}
		// Allow skipping straight to child.
		return parent.optionalPath(child)
	case syntax.OpLiteral: // x
		if SPLIT_LITERAL_INTO_RUNES {
			i := len(re.Rune)
			for i > 0 {
				i--
				parent = directory.ensureNode(re, parent)
				runes := []rune{re.Rune[i], re.Rune[i]}
				parent, child = nil, parent.linkRunes(runes, child, repeats)
			}
			return child
		} else {
			parent = directory.ensureNode(re, parent)
			parent.linkPath(string(re.Rune), child, repeats)
			return parent
		}
	case syntax.OpPlus:
		if len(re.Sub) != 1 {
			panic("Unable to handle OpPlus with 2+ Sub options")
		} else if parent == nil {
			// Only allow looping through child.
			directory.linker(child, child, re.Sub[0], true)
			// Require at least one path through re.Sub[0]
			return directory.linker(parent, child, re.Sub[0], true)
		}
		if EPSILON_EXPANSION {
			// We must not contaminate child which may be used by others.
			detour := directory.addRegexpAs(re, child)
			// Child may optionally loop back to itself.
			directory.linker(detour, detour, re.Sub[0], true)
			// Require at least one path through re.Sub[0]
			directory.linker(parent, detour, re.Sub[0], true)
			return parent
		} else {
			// We must not contaminate child which may be used by others.
			detour := child.Copy()
			// Child may optionally loop back to itself.
			directory.linker(detour, detour, re.Sub[0], true)
			// Require at least one path through re.Sub[0]
			return directory.linker(parent, detour, re.Sub[0], true)
		}
	case syntax.OpQuest: // x?
		if len(re.Sub) != 1 {
			panic("Unable to handle OpQuest with 2+ Sub options")
		}
		// Offer link to alternate path.
		parent = directory.linker(parent, child, re.Sub[0], repeats)
		// Mark the path to child as optional.
		return parent.optionalPath(child)
	case syntax.OpStar: // x*
		if len(re.Sub) != 1 {
			panic("Unable to handle OpStar with 2+ Sub options")
		} else if parent == nil {
			// Only allow looping through child.
			return directory.linker(child, child, re.Sub[0], true)
		}
		if EPSILON_EXPANSION {
			// We must not contaminate parent which may be used by others.
			detour := directory.addRegexpAs(re, child)
			// Create a branching path to the detour via re.Sub[0]...
			directory.linker(parent, detour, re.Sub[0], true)
			// ...which repeats.
			directory.linker(detour, detour, re.Sub[0], true)
			// Ensure it is possible to go straight from parent to child.
			return directory.merge(parent, child)
		} else {
			// We must not contaminate child which may be used by others.
			detour := child.Copy()
			// Allow looping through (copied) child.
			directory.linker(detour, detour, re.Sub[0], true)
			// Ensure it is possible to go straight from parent to child.
			return parent.optionalPath(detour)
		}
	}
	panic(fmt.Sprintf("Unsupported instruction: %d", re.Op))
}

func (directory *dfaDirectory) merge(a *reTrieNode, b *reTrieNode) *reTrieNode {
	mergedId := a.id | b.id
	mergedDfaNode, exists := directory.table[mergedId]
	if exists {
		return mergedDfaNode
	}
	result := directory.partialMerge(a, b)
	result.mergeNode(a)
	result.mergeNode(b)
	return result
}

func (directory *dfaDirectory) partialMerge(a *reTrieNode, b *reTrieNode) *reTrieNode {
	mergedId := a.id | b.id
	mergedDfaNode, exists := directory.table[mergedId]
	if exists {
		return mergedDfaNode
	}
	result := newReTrieNode(directory, mergedId, a.rootNode.Copy())
	directory.table[mergedId] = result
	result.rootNode.Union(b.rootNode)
	return result
}

func (directory *dfaDirectory) split(link *reTrieLink) *reTrieLink {
	prefixRune, prefixRuneSize := utf8.DecodeRuneInString(link.prefix)
	parent := directory.ensureNode(nil, nil)
	// TODO: Remove cast.
	child := link.node.(*reTrieNode)
	parent.linkPath(link.prefix[prefixRuneSize:], child, false)
	return newReTrieLinkFromRunes([]rune{prefixRune, prefixRune}, parent)
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

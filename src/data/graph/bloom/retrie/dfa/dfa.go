package dfa

import (
	"fmt"
	"regexp/syntax"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

const LOG_INFO = false

var anyRunes = []rune{
	'a', 'z',
	' ', ' ',
	'-', '-',
	'\'', '\'',
}

type dfaDirectory struct {
	table      map[dfaId]*dfaNode
	goal       *node.Node
	nfa2dfa    []dfaId        // NFA ID -> DFA ID
	nfaEdges   []*dfaNodeEdge // NFA ID -> DFA edge (there is only ever 1)
	sweepEpoch int            // Increment with each BFS or DFS traversal.
}

// Note: Library will panic if there are >64 nodes.
type dfaId = uint64

func Dfa(regularExpression string, weight weight.Weight) *dfaNode {
	re, err := syntax.Parse(regularExpression, syntax.Perl)
	if err != nil {
		panic(err)
	}
	re = re.Simplify()
	goal := node.NewNode(weight)
	return Process(re, goal)
}

func Process(re *syntax.Regexp, goal *node.Node) *dfaNode {
	prog, err := syntax.Compile(re)
	if err != nil {
		panic(err)
	}
	directory := newDfaDirectory(len(prog.Inst), goal)
	// 1a. Perform ε expansion to find the DFA alias for each NFA instruction.
	// 1b. Save edges associated with the NFA node.
	// 2. Populate outgoing edges for NFAs.
	directory.init(prog.Inst)
	root := directory.table[directory.nfa2dfa[prog.Start]]
	// 3. Expand edges for DFAs.
	// 4. Populate incoming edges for DFAs.
	directory.expandFrom(directory.startEpoch(), root)
	return root
}

func newDfaDirectory(nodeCount int, goal *node.Node) *dfaDirectory {
	if nodeCount > 64 {
		panic(">64 states are unsupported")
	}
	return &dfaDirectory{
		table:    make(map[dfaId]*dfaNode, nodeCount),
		goal:     goal,
		nfa2dfa:  make([]dfaId, nodeCount),
		nfaEdges: make([]*dfaNodeEdge, nodeCount),
	}
}

func (directory *dfaDirectory) init(instructions []syntax.Inst) {
	var epsilonExpand func(root *dfaNode, cursor uint32)
	epsilonExpand = func(root *dfaNode, cursor uint32) {
		nextId := dfaId(1 << cursor)
		if root.id&nextId != 0 {
			panic("Cycle detected in ε expansion")
		}
		root.id |= nextId
		root.sources = append(root.sources, uint8(cursor))
		instruction := instructions[cursor]
		if instruction.Op == syntax.InstMatch {
			root.nodeNode = directory.goal.Copy() // Matching.
		} else {
			root.nodeNode = node.NewNode() // Non-matching.
		}
		switch instruction.Op {
		case syntax.InstAlt, syntax.InstAltMatch:
			epsilonExpand(root, instruction.Out)
			epsilonExpand(root, instruction.Arg)
		case syntax.InstFail, syntax.InstMatch, syntax.InstRune, syntax.InstRuneAny, syntax.InstRuneAnyNotNL, syntax.InstRune1:
			// No ε Out.
		case syntax.InstCapture, syntax.InstEmptyWidth, syntax.InstNop:
			epsilonExpand(root, instruction.Out)
		default:
			panic(fmt.Sprintf("Unsupported ε expansion operation: %s", instruction.Op))
		}
	}
	// 1a. Perform ε expansion to find the DFA alias for each NFA instruction.
	// 1b. Save edges associated with the NFA node.
	for nfaId := range instructions {
		root := newDfaNode(directory)
		epsilonExpand(root, uint32(nfaId))
		directory.table[root.id] = root
		directory.nfa2dfa[nfaId] = root.id
	}
	// 2. Populate outgoing edges for NFAs.
	for nfaId, instruction := range instructions {
		if len(instruction.Rune) == 0 {
			continue
		}
		edge := &dfaNodeEdge{
			destination: directory.nfa2dfa[instruction.Out],
		}
		directory.nfaEdges[nfaId] = edge
		switch instruction.Op {
		case syntax.InstRune, syntax.InstRune1:
			edge.runes = instruction.Rune
		case syntax.InstRuneAny, syntax.InstRuneAnyNotNL:
			edge.runes = anyRunes
		default:
			panic(fmt.Sprintf("Unsupported init operand: %s", instruction.Op))
		}
	}
}

func (directory *dfaDirectory) startEpoch() int {
	directory.sweepEpoch += len(directory.table)
	return directory.sweepEpoch
}

func (directory *dfaDirectory) expandFrom(depth int, cursor *dfaNode) int {
	if !cursor.maybeVisit(depth) {
		if cursor.visitDepth != 0 {
			return depth - cursor.visitDepth
		}
		return 0
	}
	// 3. Expand edges for DFAs.
	for _, edge := range cursor.initOutgoing() {
		destinationDfa := directory.table[edge.destination]
		cycleLength := directory.expandFrom(depth+1, destinationDfa)
		cursor.maskRunes(edge.runes, destinationDfa.nodeNode)
		if cycleLength > 0 {
			cursor.nodeNode.RepeatLengthMask(cycleLength)
		}
	}
	cursor.finishVisit()
	return 0
}

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
	debugInst  []syntax.Inst  // Only used by GraphVizString.
	debugOrig  string         // Only used by GraphVizString.
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
	return Process(regularExpression, re, goal)
}

func Process(regularExpression string, re *syntax.Regexp, goal *node.Node) *dfaNode {
	prog, err := syntax.Compile(re)
	if err != nil {
		panic(err)
	}
	directory := newDfaDirectory(prog.Inst, goal)
	// TODO: Clean this up.
	directory.debugOrig = regularExpression
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

func newDfaDirectory(instructions []syntax.Inst, goal *node.Node) *dfaDirectory {
	nodeCount := len(instructions)
	if nodeCount > 64 {
		panic(">64 states are unsupported")
	}
	return &dfaDirectory{
		table:     make(map[dfaId]*dfaNode, nodeCount),
		goal:      goal,
		nfa2dfa:   make([]dfaId, nodeCount),
		nfaEdges:  make([]*dfaNodeEdge, nodeCount),
		debugInst: instructions,
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
		var runes []rune
		switch instruction.Op {
		case syntax.InstRune, syntax.InstRune1:
			runes = instruction.Rune
			// Normalize runes.
			// NB: The original runes slice shares memory(?) with the source program.
			if len(runes) == 1 {
				runes = []rune{runes[0], runes[0]}
			}
		case syntax.InstRuneAny, syntax.InstRuneAnyNotNL:
			runes = anyRunes
		default:
			panic(fmt.Sprintf("Unsupported init operand: %s", instruction.Op))
		}
		edge := newDfaNodeEdge(
			runes,
			directory.nfa2dfa[instruction.Out],
		)
		directory.nfaEdges[nfaId] = edge
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
	cycles := []int{}
	for _, edge := range cursor.initOutgoing() {
		destinationDfa := directory.table[edge.destination]
		//cursor.maskEdge(edge, destinationDfa.nodeNode)
		cycleLength := directory.expandFrom(depth+1, destinationDfa)
		cursor.maskEdge(edge, destinationDfa.nodeNode)
		if cycleLength > 0 {
			cycles = append(cycles, cycleLength)
		}
	}
	// Mark cycles after masking all edges.
	for _, cycle := range cycles {
		cursor.nodeNode.RepeatLengthMask(cycle)
	}
	cursor.finishVisit()
	return 0
}

func (directory *dfaDirectory) addDfaNodes(first dfaId, second dfaId) {
	id := first | second
	_, exists := directory.table[id]
	if exists {
		return
	}
	result := newDfaNode(directory)
	directory.table[id] = result
	result.id = id
	firstDfa := directory.table[first]
	secondDfa := directory.table[second]
	if firstDfa.nodeNode.Matches() || secondDfa.nodeNode.Matches() {
		result.nodeNode = directory.goal.Copy()
	} else {
		result.nodeNode = node.NewNode()
	}
	remainingSources := id
	// Attempt to bootstrap outgoing edges.
	firstLen := len(firstDfa.outgoing)
	secondLen := len(secondDfa.outgoing)
	if firstLen+secondLen > 0 {
		if secondLen > firstLen {
			// Prefer to inherit the larger outgoing list.
			firstDfa = secondDfa
			firstLen, secondLen = secondLen, firstLen
		}
		result.outgoing = make(dfaNodeEdgeList, firstLen, firstLen+secondLen)
		copy(result.outgoing, firstDfa.outgoing)
		remainingSources = id - firstDfa.id
	}
	result.sources = []uint8{}
	source := uint8(0)
	for (1 << source) <= remainingSources {
		if (1<<source)&remainingSources != 0 {
			result.sources = append(result.sources, source)
		}
		source++
	}
}

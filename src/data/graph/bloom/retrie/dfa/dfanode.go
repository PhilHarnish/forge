package dfa

import (
	"container/heap"
	"fmt"
	"regexp/syntax"
	"strconv"
	"strings"
	"unicode"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type dfaNode struct {
	id          dfaId
	directory   *dfaDirectory
	nodeNode    *node.Node
	outgoing    dfaNodeEdgeList
	incoming    dfaNodeEdgeList
	outMask     mask.Mask
	sources     []uint8 // An NFA ID is never >64.
	lastVisited int     // Monotonically increases.
	visitDepth  int     // Reset when going back out.
}

type dfaNodeEdge struct {
	runes       []rune
	destination dfaId
	edgeMask    mask.Mask
}
type dfaNodeEdgeList []*dfaNodeEdge

func newDfaNode(directory *dfaDirectory) *dfaNode {
	return &dfaNode{
		directory: directory,
		incoming:  dfaNodeEdgeList{},
	}
}

func newDfaNodeEdge(runes []rune, destination dfaId) *dfaNodeEdge {
	return &dfaNodeEdge{
		runes:       runes,
		destination: destination,
		edgeMask:    runesMask(runes),
	}
}

func (root *dfaNode) String() string {
	return node.Format(fmt.Sprintf("DFA{%s}", dfaIdToString(root.id)), root.nodeNode)
}

func (root *dfaNode) Items(generator node.NodeGenerator) node.NodeItems {
	return newDfaItems(root.directory, root, generator)
}

func (root *dfaNode) Root() *node.Node {
	return root.nodeNode
}

func (root *dfaNode) GraphVizString() string {
	acc := []string{
		"digraph G {",
		fmt.Sprintf(`	label="/%s/";`, root.directory.debugOrig),
		"	subgraph nfa {",
		"		node [shape=record];",
	}
	nfa := []string{}
	for i, instruction := range root.directory.debugInst {
		label := strings.ReplaceAll(instruction.String(), " -> ", "|")
		label = strings.ReplaceAll(label, `"`, `'`)
		if instruction.Op == syntax.InstMatch || instruction.Op == syntax.InstFail {
			label += "|"
		} else {
			destination := instruction.Out
			edge := root.directory.nfaEdges[i]
			edgeLabel := "ε"
			style := " style=dotted"
			if edge != nil {
				edgeLabel = mask.MaskString(edge.edgeMask, 0)
				style = ""
			}
			acc = append(acc, fmt.Sprintf(`		nfa:n%d:ne -> nfa:n%d:n [labeldistance=2 headlabel="%s"%s];`,
				i, destination, edgeLabel, style))
			if instruction.Op == syntax.InstAlt || instruction.Op == syntax.InstAltMatch {
				acc = append(acc, fmt.Sprintf(`		nfa:n%d:ne -> nfa:n%d:n [labeldistance=2 headlabel="%s"%s];`,
					i, instruction.Arg, edgeLabel, style))
			}
		}
		nfa = append(nfa, fmt.Sprintf(`{<n%d>%d|%s}`, i, i, label))
	}
	acc = append(acc,
		fmt.Sprintf(`		nfa [label="%s"];`, strings.Join(nfa, "|")),
		"	}",
	)
	root.graphVizEdgeStrings(&acc, root.directory.startEpoch())
	acc = append(acc, "}")
	return strings.Join(acc, "\n")
}

func (root *dfaNode) graphVizEdgeStrings(acc *[]string, sweep int) {
	if !root.maybeVisit(sweep) {
		return
	}
	if root.nodeNode.Matches() {
		*acc = append(*acc, fmt.Sprintf(`	"%s" [shape=doublecircle];`, dfaIdToString(root.id)))
	} else {
		*acc = append(*acc, fmt.Sprintf("	// %s does not match", dfaIdToString(root.id)))
	}
	for _, edge := range root.outgoing {
		*acc = append(*acc, fmt.Sprintf(`	"%s" -> "%s" [label="%s"];`,
			dfaIdToString(root.id), dfaIdToString(edge.destination),
			edge.String()))
		destination, ok := root.directory.table[edge.destination]
		if ok {
			sweep++
			destination.graphVizEdgeStrings(acc, sweep)
		} else {
			*acc = append(*acc, fmt.Sprintf(`	"%s" [color=red];`, dfaIdToString(root.id)))
		}
	}
}

const OPTIMIZED = false

func (root *dfaNode) maybeVisit(depth int) bool {
	if root.visitDepth != 0 {
		return false
	}
	if OPTIMIZED && root.lastVisited > root.directory.sweepEpoch {
		return false
	}
	root.lastVisited = depth
	root.visitDepth = depth
	return true
}

func (root *dfaNode) finishVisit() {
	root.visitDepth = 0
}

func (root *dfaNode) initOutgoing() dfaNodeEdgeList {
	if root.outgoing != nil && root.sources == nil {
		return root.outgoing
	}
	duplicates := mask.Mask(0)
	for _, source := range root.sources {
		edge := root.directory.nfaEdges[source]
		if edge == nil {
			continue
		}
		edgeMask := edge.edgeMask
		duplicates |= root.outMask & edgeMask
		root.outMask |= edgeMask
		root.outgoing = append(root.outgoing, edge)
	}
	if duplicates != 0 {
		root.splitEdges(duplicates)
	}
	root.sources = nil
	return root.outgoing
}

func (root *dfaNode) splitEdges(duplicates mask.Mask) {
	original := root.outgoing
	root.outgoing = make(dfaNodeEdgeList, 0, len(original)*2)
	heap.Init(&original)
	newNodes := []dfaId{}
	for len(original) > 0 {
		first := original.Next()
		// First, confirm there are any remaining edges to compare with.
		if len(original) == 0 {
			root.outgoing = append(root.outgoing, first) // Finished; add and continue.
			continue
		}
		// Next, confirm this edge was problematic.
		if first.edgeMask&duplicates == 0 {
			root.outgoing = append(root.outgoing, first) // No issue; add and continue.
			continue
		}
		// Next, split any edges with multiple rune blocks.
		if len(first.runes) > 2 {
			runes := first.runes
			for i := 0; i < len(runes); i += 2 {
				batchEdge := newDfaNodeEdge(runes[i:i+1], first.destination)
				batchMask := batchEdge.edgeMask
				if batchMask&duplicates == 0 {
					// This batch is OK.
					root.outgoing = append(root.outgoing, batchEdge)
				} else {
					// This batch needs to be reprocessed.
					heap.Push(&original, batchEdge)
				}
			}
			continue
		}
		// Edge has exactly one batch; this is a confirmed hit.
		second := original.Next()
		if first.destination == second.destination {
			// Both edges go to the same place; return super-set of the range.
			batch0 := []rune{
				min(first.runes[0], second.runes[0]),
				max(first.runes[1], second.runes[1]),
			}
			root.outgoing = append(root.outgoing, newDfaNodeEdge(batch0, first.destination))
			continue
		}
		if first.edgeMask&second.edgeMask == 0 {
			panic("Heap should have brought overlapping edges together")
		}
		if first.runes[0] < second.runes[0] {
			// Batch #1 will begin and end before second edge starts.
			batch1 := []rune{first.runes[0], second.runes[0] - 1}
			root.outgoing = append(root.outgoing, newDfaNodeEdge(batch1, first.destination))
		}
		// The second batch is the portion which overlaps.
		overlapEnd := min(first.runes[1], second.runes[1])
		batch2 := []rune{second.runes[0], overlapEnd}
		newNodes = append(newNodes, first.destination, second.destination)
		overlapEdge := newDfaNodeEdge(batch2, first.destination|second.destination)
		if len(original) > 0 && original[0].edgeMask&overlapEdge.edgeMask != 0 {
			// Unfortunately, this overlaping portion overlaps with yet-more edges.
			// Return for further processing.
			heap.Push(&original, overlapEdge)
		} else {
			root.outgoing = append(root.outgoing, overlapEdge)
		}
		// Assign the remaining rune range depending on which group is larger.
		if first.runes[1] != second.runes[1] {
			// Guess that the first rune is larger.
			remainderEnd := first.runes[1]
			destination := first.destination
			if first.runes[1] < second.runes[1] { // Update if wrong.
				remainderEnd = second.runes[1]
				destination = second.destination
			}
			batch3 := []rune{overlapEnd + 1, remainderEnd}
			remainingEdge := newDfaNodeEdge(batch3, destination)
			if len(original) > 0 && original[0].edgeMask&remainingEdge.edgeMask != 0 {
				// Unfortunately, this remaining portion overlaps with yet-more edges.
				// Return for further processing.
				heap.Push(&original, remainingEdge)
			} else {
				root.outgoing = append(root.outgoing, remainingEdge)
			}
		} // Else: Both ended at the same time; there isn't a 3rd batch.
	}
	for i := 0; i < len(newNodes); i += 2 {
		root.directory.addDfaNodes(newNodes[i], newNodes[i+1])
	}
}

func (root *dfaNode) maskEdge(edge *dfaNodeEdge, child *node.Node) {
	root.nodeNode.MaskEdgeMaskToChild(edge.edgeMask, child)
}

func runesMask(runes []rune) mask.Mask {
	if len(runes) == 1 {
		edgeMask, err := mask.AlphabetMask(runes[0])
		if err != nil {
			panic(err)
		}
		return edgeMask
	}
	i := 0
	result := mask.Mask(0)
	for i < len(runes) {
		start := runes[i]
		end := runes[i+1]
		edgeMask, err := mask.AlphabetMaskRange(start, end)
		if err == nil {
			result |= edgeMask
		} else if unicode.IsLetter(start) && unicode.IsLetter(end) {
			// A letter is a reasonable character to attempt; skip.
		} else if unicode.IsNumber(start) && unicode.IsNumber(end) {
			// A number is a reasonable character to attempt; skip.
		} else if start == '_' && end == '_' {
			// _ is a reasonable character to attempt; skip.
		} else {
			panic(err)
		}
		i += 2
	}
	return result
}

func dfaIdToString(id dfaId) string {
	children := []string{}
	binary := strconv.FormatUint(id, 2)
	position := int64(0)
	for i := len(binary) - 1; i >= 0; i-- {
		if binary[i] == '1' {
			children = append(children, strconv.FormatInt(position, 10))
		}
		position++
	}
	return strings.Join(children, ",")
}

func (root *dfaNodeEdge) String() string {
	maskString := mask.MaskString(runesMask(root.runes), 0)
	if len(maskString) == 1 {
		return maskString
	}
	return fmt.Sprintf("[%s]", maskString)
}

func (edges dfaNodeEdgeList) Len() int {
	return len(edges)
}

func (edges dfaNodeEdgeList) Less(i int, j int) bool {
	if edges[i].runes[0] == edges[j].runes[0] {
		return edges[i].runes[1] < edges[j].runes[1]
	}
	return edges[i].runes[0] < edges[j].runes[0]
}

func (h dfaNodeEdgeList) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *dfaNodeEdgeList) Push(item interface{}) {
	*h = append(*h, item.(*dfaNodeEdge))
}

func (h *dfaNodeEdgeList) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *dfaNodeEdgeList) Next() *dfaNodeEdge {
	return heap.Pop(h).(*dfaNodeEdge)
}

func min(a rune, b rune) rune {
	if a < b {
		return a
	}
	return b
}

func max(a rune, b rune) rune {
	if a > b {
		return a
	}
	return b
}

package dfa

import (
	"fmt"
	"strconv"
	"strings"
	"unicode"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type dfaNode struct {
	directory   *dfaDirectory
	nodeNode    *node.Node
	outgoing    dfaNodeEdgeList
	outMask     mask.Mask
	id          dfaId
	sources     []uint8 // An NFA ID is never >64.
	lastVisited int     // Monotonically increases.
	visitDepth  int     // Reset when going back out.
}

type dfaNodeEdge struct {
	runes       []rune
	destination dfaId
	edgeMask    mask.Mask
}
type dfaNodeEdgeList = []*dfaNodeEdge

func newDfaNode(directory *dfaDirectory) *dfaNode {
	return &dfaNode{
		directory: directory,
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

func (root *dfaNode) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return newDfaItems(root.directory, root, acceptor)
}

func (root *dfaNode) Root() *node.Node {
	return root.nodeNode
}

func (root *dfaNode) GraphVizString() string {
	acc := []string{
		"digraph G {",
	}
	root.graphVizEdgeStrings(&acc, root.directory.startEpoch())
	acc = append(acc, "}")
	return strings.Join(acc, "\n")
}

func (root *dfaNode) graphVizEdgeStrings(acc *[]string, sweep int) {
	if !root.maybeVisit(sweep) {
		return
	}
	if root.nodeNode.Matches() {
		*acc = append(*acc, fmt.Sprintf(`	"%s" [shape=doublecircle]`, dfaIdToString(root.id)))
	} else {
		*acc = append(*acc, fmt.Sprintf("	// %s does not match", dfaIdToString(root.id)))
	}
	for _, edge := range root.outgoing {
		*acc = append(*acc, fmt.Sprintf(`	"%s" -> "%s" [label="%s"]`,
			dfaIdToString(root.id), dfaIdToString(edge.destination),
			edge.String()))
		destination, ok := root.directory.table[edge.destination]
		if ok {
			sweep++
			destination.graphVizEdgeStrings(acc, sweep)
		} else {
			*acc = append(*acc, fmt.Sprintf(`	"%s" [color=red]`, dfaIdToString(root.id)))
		}
	}
}

func (root *dfaNode) maybeVisit(depth int) bool {
	if root.lastVisited > root.directory.sweepEpoch {
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
	if root.outgoing != nil {
		panic("Duplicate visit")
	}
	for _, source := range root.sources {
		edge := root.directory.nfaEdges[source]
		if edge != nil {
			root.outgoing = append(root.outgoing, edge)
		}
	}
	root.sources = nil
	return root.outgoing
}

func (root *dfaNode) maskEdge(edge *dfaNodeEdge, child *node.Node) {
	edgeMask := edge.edgeMask
	duplicates := root.outMask & edgeMask
	if duplicates != 0 {
		// Split edges.
	}
	root.outMask |= edgeMask
	root.nodeNode.MaskEdgeMaskToChild(edgeMask, child)
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

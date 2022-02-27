package dfa

import "github.com/philharnish/forge/src/data/graph/bloom/node"

type dfaItems struct {
	directory  *dfaDirectory
	root       *dfaNode
	edgeIndex  int
	runeIndex  int
	runeOffset rune
}

func newDfaItems(directory *dfaDirectory, root *dfaNode, acceptor node.NodeAcceptor) node.NodeItems {
	return &dfaItems{
		directory: directory,
		root:      root,
	}
}

func (items *dfaItems) HasNext() bool {
	return items.edgeIndex < len(items.root.outgoing)
}

func (items *dfaItems) Next() (string, node.NodeIterator) {
	edge := items.root.outgoing[items.edgeIndex]
	path, iterator := maybeMergeTraversal(items.directory, edge)
	if iterator != nil {
		items.edgeIndex++
		return path, iterator
	}
	start := edge.runes[items.runeIndex]
	path = string(start + items.runeOffset)
	items.runeOffset++
	if start+items.runeOffset > edge.runes[items.runeIndex+1] {
		items.runeIndex += 2
		items.runeOffset = 0
	}
	if items.runeIndex >= len(edge.runes) {
		items.edgeIndex++
	}
	return path, items.directory.table[edge.destination]
}

func maybeMergeTraversal(directory *dfaDirectory, edge *dfaNodeEdge) (string, *dfaNode) {
	path := ""
	var result *dfaNode = nil
	for len(edge.runes) == 1 {
		path += string(edge.runes[0])
		result = directory.table[edge.destination]
		if result.nodeNode.Matches() {
			break
		} else if len(result.outgoing) == 1 {
			edge = result.outgoing[0]
		} else {
			break
		}
	}
	return path, result
}

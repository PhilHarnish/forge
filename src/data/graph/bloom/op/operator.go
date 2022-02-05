package op

import (
	"container/heap"
	"fmt"
	"unicode/utf8"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

func (op *operator) Process(acceptor node.NodeAcceptor, operands []node.NodeIterator) operatorEdgeHeap {
	if op.processMethod == parallel {
		edgeThreshold := 0
		if op.edgeThreshold == allEdges {
			edgeThreshold = len(operands)
		}
		return processParallel(acceptor, operands, op.maxWeightPolicy == useSmallest, edgeThreshold)
	} else {
		panic(fmt.Sprintf("Unsupported process method: %v", op.processMethod))
	}
}

type operator struct {
	template        string
	processMethod   processMethod
	maxWeightPolicy maxWeightPolicy
	edgeThreshold   edgeThreshold
}

type processMethod int

const (
	parallel processMethod = iota
	sequential
)

type maxWeightPolicy int

const (
	useLargest maxWeightPolicy = iota
	useSmallest
)

type edgeThreshold int

const (
	allEdges edgeThreshold = iota
	anyEdges
)

var andOperator = &operator{
	template:        "AND(%s)",
	processMethod:   parallel,
	maxWeightPolicy: useSmallest,
	edgeThreshold:   allEdges,
}

var orOperator = &operator{
	template:        "OR(%s)",
	processMethod:   parallel,
	maxWeightPolicy: useLargest,
	edgeThreshold:   anyEdges,
}

var concatOperator = &operator{
	template:        "CONCAT(%s)",
	processMethod:   sequential,
	maxWeightPolicy: useLargest,
	edgeThreshold:   anyEdges,
}

var joinOperator = &operator{
	template:        "JOIN('%s', %s)",
	processMethod:   sequential,
	maxWeightPolicy: useLargest,
	edgeThreshold:   anyEdges,
}

type operatorEdge struct {
	path     string
	operands []node.NodeIterator
	weight   weight.Weight
}

type operatorEdgeHeap []*operatorEdge

func processParallel(acceptor node.NodeAcceptor, operands []node.NodeIterator,
	minWeight bool, edgeThreshold int) operatorEdgeHeap {
	// Create max.SIZE number of buckets for the edges we find.
	// This enables O(1) lookup later.
	outgoingEdgeList := [mask.SIZE]operatorEdge{}
	// Record outgoing edges when they exceed `edgeThreshold`.
	availableOutgoingEdges := operatorEdgeHeap{}
	for _, operand := range operands {
		items := operand.Items(acceptor)
		for items.HasNext() {
			path, item := items.Next()
			edge, size := utf8.DecodeRuneInString(path)
			if size < len(path) {
				panic("Multi-rune edges are not supported")
			}
			// NB: We assume `err` is nil here.
			position, _ := mask.Position(edge)
			outgoingEdge := outgoingEdgeList[position]
			itemWeight := item.Root().MaxWeight
			if len(outgoingEdge.operands) == 0 {
				// First operator to use this edge.
				outgoingEdge.path = path
				outgoingEdge.weight = itemWeight
			} else if (minWeight && itemWeight < outgoingEdge.weight) ||
				(!minWeight && itemWeight > outgoingEdge.weight) {
				// Duplicate operator with this edge.
				outgoingEdge.weight = itemWeight
			}
			outgoingEdge.operands = append(outgoingEdgeList[position].operands, item)
			if len(outgoingEdge.operands) >= edgeThreshold {
				// Once enough operands share the edge, add to availableOutgoingEdges.
				availableOutgoingEdges = append(availableOutgoingEdges, &outgoingEdge)
			}
		}
	}
	heap.Init(&availableOutgoingEdges)
	return availableOutgoingEdges
}

func (h operatorEdgeHeap) Len() int {
	return len(h)
}

func (h operatorEdgeHeap) Less(i int, j int) bool {
	// NB: "Less" is inverted to implement a max-heap.
	return h[i].weight > h[j].weight
}

func (h operatorEdgeHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *operatorEdgeHeap) Push(item interface{}) {
	*h = append(*h, item.(*operatorEdge))
}

func (h *operatorEdgeHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *operatorEdgeHeap) Next() *operatorEdge {
	return heap.Pop(h).(*operatorEdge)
}

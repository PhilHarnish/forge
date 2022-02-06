package op

import (
	"container/heap"
	"unicode/utf8"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

func (op *operator) Process(acceptor node.NodeAcceptor, operands []node.NodeIterator) operatorEdgeHeap {
	if op.processMethod == parallel {
		return processParallel(acceptor, operands, op.maxWeightPolicy == useSmallest, op.edgePolicy)
	} else {
		return processSequential(acceptor, operands, op.maxWeightPolicy == useSmallest, op.edgePolicy)
	}
}

type operator struct {
	template        string
	processMethod   processMethod
	maxWeightPolicy maxWeightPolicy
	edgePolicy      edgePolicy
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

type edgePolicy int

const (
	allEdges edgePolicy = iota
	anyEdges
)

var andOperator = &operator{
	template:        "AND(%s)",
	processMethod:   parallel,
	maxWeightPolicy: useSmallest,
	edgePolicy:      allEdges,
}

var orOperator = &operator{
	template:        "OR(%s)",
	processMethod:   parallel,
	maxWeightPolicy: useLargest,
	edgePolicy:      anyEdges,
}

var concatOperator = &operator{
	template:        "CONCAT(%s)",
	processMethod:   sequential,
	maxWeightPolicy: useLargest,
	edgePolicy:      anyEdges,
}

type operatorEdge struct {
	path     string
	operands []node.NodeIterator
	weight   weight.Weight
}

type operatorEdgeHeap []*operatorEdge

func processParallel(acceptor node.NodeAcceptor, operands []node.NodeIterator,
	minWeight bool, edgePolicy edgePolicy) operatorEdgeHeap {
	nOperands := len(operands)
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
			outgoingEdge := &outgoingEdgeList[position]
			itemWeight := item.Root().MaxWeight
			if len(outgoingEdge.operands) == 0 {
				// First operator to use this edge.
				outgoingEdge.path = path
				outgoingEdge.weight = itemWeight
			} else if (minWeight && itemWeight < outgoingEdge.weight) ||
				(!minWeight && itemWeight > outgoingEdge.weight) {
				// Duplicate operator with this edge; update weight.
				outgoingEdge.weight = itemWeight
			}
			outgoingEdge.operands = append(outgoingEdge.operands, item)
			if edgePolicyIsValid(edgePolicy, outgoingEdge.operands, nOperands) {
				// If append is allowed, add to availableOutgoingEdges.
				availableOutgoingEdges = append(availableOutgoingEdges, outgoingEdge)
			}
		}
	}
	heap.Init(&availableOutgoingEdges)
	return availableOutgoingEdges
}

func edgePolicyIsValid(edgePolicy edgePolicy, operands []node.NodeIterator, nOperands int) bool {
	if edgePolicy == anyEdges {
		// Simply confirm this is the first time the edge was seen.
		return len(operands) == 1
	} else if len(operands) != nOperands {
		return false // "allEdges" requires an edge for every operand.
	}
	root := operands[0].Root()
	lengthsMask := root.LengthsMask
	requiredMask := root.RequireMask & mask.ALL // Ignore the UNSET bit.
	provideMask := root.ProvideMask
	allMatch := root.MatchWeight > 0
	for _, operand := range operands[1:] {
		root = operand.Root()
		lengthsMask &= root.LengthsMask             // Only consider aligned matches.
		requiredMask |= root.RequireMask            // Require whatever anyone requires.
		provideMask &= root.ProvideMask             // Only provide what everyone can.
		allMatch = allMatch && root.MatchWeight > 0 // Only valid when all have MatchWeight.
	}
	return allMatch || (lengthsMask > 1 && (requiredMask&provideMask == requiredMask))
}

func processSequential(acceptor node.NodeAcceptor, operands []node.NodeIterator,
	minWeight bool, edgePolicy edgePolicy) operatorEdgeHeap {
	availableOutgoingEdges := operatorEdgeHeap{}
	operand := operands[0]
	items := operand.Items(acceptor)
	for items.HasNext() {
		path, item := items.Next()
		outgoingEdge := &operatorEdge{}
		outgoingEdge.path = path
		outgoingEdge.operands = append(outgoingEdge.operands, item)
		availableOutgoingEdges = append(availableOutgoingEdges, outgoingEdge)
	}
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

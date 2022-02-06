package op

import (
	"container/heap"
	"fmt"
	"unicode/utf8"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

func (op *operator) process(operation *operation, acceptor node.NodeAcceptor) operatorEdgeHeap {
	if op.processMethod == parallel {
		return processParallel(operation, acceptor)
	} else {
		return processSequential(operation, acceptor)
	}
}

func (op *operator) synthesizeNode(operands []node.NodeIterator) *node.Node {
	result := node.NewNode()
	result.Union(operands[0].Root())
	switch op.edgePolicy {
	case firstOperand:
		return result
	case anyOperands:
		for _, operand := range operands[1:] {
			result.Union(operand.Root())
		}
		return result
	case allOperands:
		for _, operand := range operands[1:] {
			result.Intersection(operand.Root())
		}
		return result
	}
	panic(fmt.Sprintf("Unable to synthesize node for %v", op))
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
	firstOperand edgePolicy = iota
	allOperands
	anyOperands
)

var andOperator = &operator{
	template:        "AND(%s)",
	processMethod:   parallel,
	maxWeightPolicy: useSmallest,
	edgePolicy:      allOperands,
}

var orOperator = &operator{
	template:        "OR(%s)",
	processMethod:   parallel,
	maxWeightPolicy: useLargest,
	edgePolicy:      anyOperands,
}

var concatOperator = &operator{
	template:        "CONCAT(%s)",
	processMethod:   sequential,
	maxWeightPolicy: useLargest,
	edgePolicy:      firstOperand,
}

type operatorEdge struct {
	path     string
	operands []node.NodeIterator
	weight   weight.Weight
	node     *node.Node
}

type operatorEdgeHeap []*operatorEdge

func processParallel(operation *operation, acceptor node.NodeAcceptor) operatorEdgeHeap {
	operator := operation.operator
	operands := operation.operands
	minWeight := operator.maxWeightPolicy == useSmallest
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
			availableEdge := filterEdge(outgoingEdge, operator, nOperands)
			if availableEdge != nil {
				// If append is allowed, add to availableOutgoingEdges.
				availableOutgoingEdges = append(availableOutgoingEdges, availableEdge)
			}
		}
	}
	heap.Init(&availableOutgoingEdges)
	return availableOutgoingEdges
}

func filterEdge(edge *operatorEdge, operator *operator, nOperands int) *operatorEdge {
	operands := edge.operands
	edgePolicy := operator.edgePolicy
	if edgePolicy == anyOperands {
		// Simply confirm this is the first time the edge was seen.
		if len(operands) == 1 {
			return edge
		}
		return nil
	} else if edgePolicy != allOperands {
		panic(fmt.Sprintf("Unable to validate edge policy: %v", edgePolicy))
	} else if len(operands) != nOperands {
		return nil // "allEdges" requires an edge for every operand.
	}
	// Allow synthesized Node to be reused.
	edge.node = operator.synthesizeNode(operands)
	if edge.node.LengthsMask > 0 {
		return edge
	}
	return nil
}

func processSequential(operation *operation, acceptor node.NodeAcceptor) operatorEdgeHeap {
	operands := operation.operands
	availableOutgoingEdges := operatorEdgeHeap{}
	operand := operands[0]
	hasMoreOperands := len(operands) > 1
	items := operand.Items(acceptor)
	for items.HasNext() {
		path, item := items.Next()
		if hasMoreOperands && item.Root().LengthsMask&0b1 == 0b1 {
			// This item is a valid location to exit.
			canKeepGoing := item.Root().LengthsMask > 1
			if canKeepGoing {
				// This path branches (keep going vs continue) so use OR.
				keepGoing := make([]node.NodeIterator, len(operands))
				copy(keepGoing, operands)
				keepGoing[0] = item
				item = Or(Concat(keepGoing...), Concat(operands[1:]...))
			} else {
				// Otherwise, the path continues sequentially.
				item = Concat(operands[1:]...)
			}
		}
		outgoingEdge := &operatorEdge{
			path:     path,
			operands: []node.NodeIterator{item},
		}
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

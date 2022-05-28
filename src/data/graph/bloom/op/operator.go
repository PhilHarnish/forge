package op

import (
	"container/heap"
	"fmt"
	"unicode/utf8"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/span"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

func (op *operator) process(operation *operation, generator node.NodeGenerator) *operatorEdgeHeap {
	if op.processMethod == parallel {
		return processParallel(operation, generator)
	} else {
		return processSequential(operation, generator)
	}
}

func (op *operator) synthesizeNode(operands []node.NodeIterator) *node.Node {
	switch op.edgePolicy {
	case sequentialOperands:
		i := len(operands) - 1
		result := operands[i].Root().Copy()
		for i > 0 {
			i--
			next := operands[i].Root()
			result.MaskPrependChild(next)
		}
		return result
	case allOperands:
		result := operands[0].Root().Copy()
		for _, operand := range operands[1:] {
			result.Intersection(operand.Root())
		}
		return result
	case anyOperands:
		result := operands[0].Root().Copy()
		for _, operand := range operands[1:] {
			result.Union(operand.Root())
		}
		return result
	}
	panic(fmt.Sprintf("Unable to synthesize node for %v", op))
}

type operator struct {
	template        string
	infix           string
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
	sequentialOperands edgePolicy = iota
	allOperands
	anyOperands
)

var andOperator = &operator{
	template:        "(%s)",
	infix:           " && ",
	processMethod:   parallel,
	maxWeightPolicy: useSmallest,
	edgePolicy:      allOperands,
}

var orOperator = &operator{
	template:        "(%s)",
	infix:           " || ",
	processMethod:   parallel,
	maxWeightPolicy: useLargest,
	edgePolicy:      anyOperands,
}

var concatOperator = &operator{
	template:        "(%s)",
	infix:           " + ",
	processMethod:   sequential,
	maxWeightPolicy: useLargest,
	edgePolicy:      sequentialOperands,
}

type operatorEdge struct {
	path       string
	operands   []node.NodeIterator
	generators []node.NodeGenerator
	weight     weight.Weight
	node       *node.Node
}

type operatorEdgeHeap []*operatorEdge

func processParallel(operation *operation, generator node.NodeGenerator) *operatorEdgeHeap {
	operator := operation.operator
	operands := operation.operands
	generators := operation.getGenerators(generator)
	minWeight := operator.maxWeightPolicy == useSmallest
	nOperands := len(operands)
	// Create max.SIZE number of buckets for the edges we find.
	// This enables O(1) lookup later.
	outgoingEdgeList := [mask.SIZE]operatorEdge{}
	availableOutgoingEdges := operatorEdgeHeap{}
	for i, operand := range operands {
		itemsGenerator := generators[i]
		items := itemsGenerator.Items(operand)
		for items.HasNext() {
			path, item := items.Next()
			edge, _ := utf8.DecodeRuneInString(path)
			// NB: We assume `err` is nil here.
			position, _ := mask.Position(edge)
			outgoingEdge := &outgoingEdgeList[position]
			itemWeight := item.Root().MaxWeight
			if len(outgoingEdge.operands) == 0 {
				// First operator to use this edge.
				outgoingEdge.path = path
				outgoingEdge.weight = itemWeight
			} else {
				// Duplicate edge.
				if outgoingEdge.path != path {
					// The existing path for this edge looks different; split.
					item = outgoingEdge.updatePath(path, item)
				}
				if (minWeight && itemWeight < outgoingEdge.weight) ||
					(!minWeight && itemWeight > outgoingEdge.weight) {
					// Duplicate operator with this edge; update weight.
					outgoingEdge.weight = itemWeight
				}
			}
			outgoingEdge.operands = append(outgoingEdge.operands, item)
			outgoingEdge.generators = append(outgoingEdge.generators, itemsGenerator)
			availableEdge := filterEdge(outgoingEdge, operator, nOperands)
			if availableEdge != nil {
				// If append is allowed, add to availableOutgoingEdges.
				availableOutgoingEdges = append(availableOutgoingEdges, availableEdge)
			}
		}
	}
	heap.Init(&availableOutgoingEdges)
	return &availableOutgoingEdges
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

func processSequential(operation *operation, generator node.NodeGenerator) *operatorEdgeHeap {
	operands := operation.operands
	if len(operands) <= 1 {
		panic("Sequential processing unecessary.")
	}
	availableOutgoingEdges := operatorEdgeHeap{}
	operand := operands[0]
	generators := operation.getGenerators(generator)
	items := generators[0].Items(operand)
	for items.HasNext() {
		path, item := items.Next()
		if item.Root().Matches() {
			// This item is a valid location to exit.
			canKeepGoing := item.Root().LengthsMask > 1
			if canKeepGoing {
				// This path branches so create fork to both {item, exit}.
				item = operation.fork(item)
			} else {
				// Otherwise, the path continues sequentially.
				item = operation.slice(1, len(operands))
			}
		} else {
			// Path does not fork but must still keep going.
			item = operation.substitute(0, item)
		}
		outgoingEdge := &operatorEdge{
			path:     path,
			operands: []node.NodeIterator{item},
			// NB: `generators` is nil since there is always 1 outgoing choice.
		}
		availableOutgoingEdges = append(availableOutgoingEdges, outgoingEdge)
	}
	return &availableOutgoingEdges
}

func (edge *operatorEdge) updatePath(path string, item node.NodeIterator) node.NodeIterator {
	prefix := commonPrefix(edge.path, path)
	if prefix != edge.path {
		// Fix existing operands.
		originalSuffix := edge.path[len(prefix):]
		for i, operand := range edge.operands {
			edge.operands[i] = span.NewSpan(originalSuffix, operand)
		}
	}
	if prefix != path {
		// Fix provided path.
		newSuffix := path[len(prefix):]
		item = span.NewSpan(newSuffix, item)
	}
	edge.path = prefix
	return item
}

func commonPrefix(a string, b string) string {
	aLen := len(a)
	bLen := len(b)
	smallest := a
	if bLen < aLen {
		smallest = b
	}
	for i := range smallest {
		if a[i] != b[i] {
			return a[:i]
		}
	}
	return smallest
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

package op

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type operatorItems struct {
	generator node.NodeGenerator
	operation *operation
	edges     *operatorEdgeHeap
}

func newOperatorItems(generator node.NodeGenerator, operation *operation) *operatorItems {
	return &operatorItems{
		generator: generator,
		operation: operation,
	}
}

func (items *operatorItems) HasNext() bool {
	return items.getHeap().Len() > 0
}

func (items *operatorItems) Next() (string, node.NodeIterator) {
	next := items.getHeap().Next()
	nextOperation := &operation{
		operator:   items.operation.operator,
		operands:   next.operands,
		generators: next.generators,
		node:       next.node, // May be `nil`.
	}
	return next.path, nextOperation
}

func (items *operatorItems) getHeap() *operatorEdgeHeap {
	if items.edges == nil {
		items.edges = items.operation.operator.process(
			items.operation, items.generator)
	}
	return items.edges
}

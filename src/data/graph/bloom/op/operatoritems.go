package op

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type operatorItems struct {
	acceptor  node.NodeAcceptor
	operation *operation
	edges     operatorEdgeHeap
}

func newOperatorItems(acceptor node.NodeAcceptor, operation *operation) *operatorItems {
	return &operatorItems{
		acceptor:  acceptor,
		operation: operation,
	}
}

func (items *operatorItems) HasNext() bool {
	edges := items.getHeap()
	return len(edges) > 0
}

func (items *operatorItems) Next() (string, node.NodeIterator) {
	next := items.edges.Next()
	if len(next.operands) == 1 {
		// Operation only needed for 1+ arguments.
		return next.path, next.operands[0]
	}
	nextOperation := &operation{
		operator: items.operation.operator,
		operands: next.operands,
		node:     next.node, // May be `nil`.
	}
	return next.path, nextOperation
}

func (items *operatorItems) getHeap() operatorEdgeHeap {
	if items.edges == nil {
		items.edges = items.operation.operator.process(
			items.operation, items.acceptor)
	}
	return items.edges
}

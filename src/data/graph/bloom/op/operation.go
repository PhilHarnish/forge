package op

import (
	"fmt"
	"strings"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type operation struct {
	operator *operator
	operands []node.NodeIterator
	node     *node.Node
}

func (op *operation) Root() *node.Node {
	if op.node == nil {
		op.node = op.operator.synthesizeNode(op.operands)
	}
	return op.node
}

func (op *operation) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return newOperatorItems(acceptor, op)
}

func (op *operation) String() string {
	return fmt.Sprintf(op.operator.template, formatOperands(op.operands))
}

func formatOperands(operands []node.NodeIterator) string {
	formatted := make([]string, len(operands))
	for i, operand := range operands {
		formatted[i] = fmt.Sprint(operand)
	}
	return strings.Join(formatted, ", ")
}

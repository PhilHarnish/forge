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
	return node.Format(
		fmt.Sprintf(op.operator.template, formatOperands(op.operator.infix, op.operands)),
		op.Root(),
	)
}

func formatOperands(infix string, operands []node.NodeIterator) string {
	formatted := make([]string, len(operands))
	for i, operand := range operands {
		operandString := fmt.Sprint(operand)
		if !strings.HasPrefix("(", operandString) && strings.Contains(operandString, " ") {
			operandString = fmt.Sprintf("(%s)", operandString)
		}
		formatted[i] = operandString
	}
	return strings.Join(formatted, infix)
}

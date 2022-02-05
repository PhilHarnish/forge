package op

import (
	"fmt"
	"strings"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type Operation interface {
	Root() *node.Node
	Items(acceptor node.NodeAcceptor) node.NodeItems
	String() string
}

func And(operands ...node.NodeIterator) Operation {
	return &operation{
		operator: andOperator,
		operands: operands,
	}
}

func Or(operands ...node.NodeIterator) Operation {
	return &operation{
		operator: orOperator,
		operands: operands,
	}
}

func Concat(operands ...node.NodeIterator) Operation {
	return &operation{
		operator: concatOperator,
		operands: operands,
	}
}

func Join(separator string, operands ...node.NodeIterator) Operation {
	panic("Join operation currently unsupported")
}

type operation struct {
	operator *operator
	operands []node.NodeIterator
}

func (op *operation) Root() *node.Node {
	panic("operator.Root() not implemented")
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

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
	return &andOperation{
		operation: operation{
			operator: andOperator,
			operands: operands,
		},
	}
}

func Or(operands ...node.NodeIterator) Operation {
	return &orOperation{
		operation: operation{
			operator: orOperator,
			operands: operands,
		},
	}
}

func Concat(operands ...node.NodeIterator) Operation {
	return &concatOperation{
		operation: operation{
			operator: concatOperator,
			operands: operands,
		},
	}
}

func Join(separator string, operands ...node.NodeIterator) Operation {
	return &joinOperation{
		operation: operation{
			operator: joinOperator,
			operands: operands,
		},
		separator: separator,
	}
}

type operation struct {
	operator *operator
	operands []node.NodeIterator
}

type andOperation struct {
	operation
}

type orOperation struct {
	operation
}

type concatOperation struct {
	operation
}

type joinOperation struct {
	operation
	separator string
}

func (op *operation) Root() *node.Node {
	panic("operator.Root() not implemented")
}

func (op *operation) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return &operatorItems{
		acceptor: acceptor,
		operator: op,
	}
}

func (op *operation) String() string {
	return fmt.Sprintf(op.operator.template, formatOperands(op.operands))
}

func (op *joinOperation) String() string {
	return fmt.Sprintf(op.operator.template, op.separator, formatOperands(op.operands))
}

func formatOperands(operands []node.NodeIterator) string {
	formatted := make([]string, len(operands))
	for i, operand := range operands {
		formatted[i] = fmt.Sprint(operand)
	}
	return strings.Join(formatted, ", ")
}

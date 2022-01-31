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
	return &and{
		operation: operation{
			template: "AND(%s)",
			operands: operands,
		},
	}
}

func Or(operands ...node.NodeIterator) Operation {
	return &or{
		operation: operation{
			template: "OR(%s)",
			operands: operands,
		},
	}
}

func Concat(operands ...node.NodeIterator) Operation {
	return &concat{
		operation: operation{
			template: "CONCAT(%s)",
			operands: operands,
		},
	}
}

func Join(separator string, operands ...node.NodeIterator) Operation {
	return &join{
		operation: operation{
			template: fmt.Sprintf("JOIN('%s', %s)", separator, "%s"),
			operands: operands,
		},
		separator: separator,
	}
}

type operation struct {
	template string
	operands []node.NodeIterator
}

type and struct {
	operation
}

type or struct {
	operation
}

type concat struct {
	operation
}

type join struct {
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
	formatted := make([]string, len(op.operands))
	for i, operand := range op.operands {
		formatted[i] = fmt.Sprint(operand)
	}
	body := strings.Join(formatted, ", ")
	return fmt.Sprintf(op.template, body)
}

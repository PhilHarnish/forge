package op

import (
	"fmt"
	"strings"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/null"
	"github.com/philharnish/forge/src/data/graph/bloom/span"
)

type Operation interface {
	Root() *node.Node
	Items(acceptor node.NodeAcceptor) node.NodeItems
	String() string
}

func And(operands ...node.NodeIterator) Operation {
	if len(operands) == 0 {
		return null.Null
	} else if len(operands) == 1 {
		return operands[0]
	}
	return &operation{
		operator: andOperator,
		operands: operands,
	}
}

func Or(operands ...node.NodeIterator) Operation {
	if len(operands) == 0 {
		return null.Null
	} else if len(operands) == 1 {
		return operands[0]
	}
	return &operation{
		operator: orOperator,
		operands: operands,
	}
}

func Concat(operands ...node.NodeIterator) Operation {
	if len(operands) == 0 {
		return null.Null
	} else if len(operands) == 1 {
		return operands[0]
	}
	return &operation{
		operator: concatOperator,
		operands: operands,
	}
}

func Join(separator string, operands ...node.NodeIterator) Operation {
	if len(operands) == 0 {
		return null.Null
	} else if len(operands) == 1 {
		return operands[0]
	}
	sep := span.NewSpan(separator)
	concatOperands := make([]node.NodeIterator, len(operands)*2-1)
	concatOperands[0] = operands[0]
	for i, operand := range operands[1:] {
		concatOperands[(i*2)+1] = sep
		concatOperands[(i*2)+2] = operand
	}
	return Concat(concatOperands...)
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

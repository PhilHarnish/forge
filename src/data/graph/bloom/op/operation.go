package op

import (
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/operator"
)

type Operation interface {
	node.NodeIterator
	String() string
}

func And(operands ...node.NodeIterator) Operation {
	return &operation{
		operator: operator.And,
		operands: operands,
	}
}

func Or(operands ...node.NodeIterator) Operation {
	return &operation{
		operator: operator.Or,
		operands: operands,
	}
}

func Concat(operands ...node.NodeIterator) Operation {
	return &operation{
		operator: operator.Concat,
		operands: operands,
	}
}

func Join(separator rune, operands ...node.NodeIterator) Operation {
	if separator == ' ' {
		return &operation{
			operator: operator.JoinWithSpace,
			operands: operands,
		}
	}
	panic(fmt.Sprintf("'%c' join separator is unsupported", separator))
}

type operation struct {
	operator operator.Operator
	operands []node.NodeIterator
}

func (op *operation) Root() *node.Node {
	panic("Root() not implemented for operations.")
}

func (op *operation) Items(acceptor node.NodeAcceptor) node.NodeItems {
	panic("Items() not implemented for operations.")
}

func (op *operation) String() string {
	formatted := make([]string, len(op.operands))
	for i, operand := range op.operands {
		formatted[i] = fmt.Sprint(operand)
	}
	return op.operator.String(formatted)
}

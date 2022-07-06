package op

import (
	"fmt"
	"strings"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type operation struct {
	operator   *operator
	operands   []node.NodeIterator
	generators []node.NodeGenerator
	node       *node.Node
	formatting bool // Used to detect cycles during formatting.
}

func (op *operation) Root() *node.Node {
	if op.node == nil {
		op.node = op.operator.synthesizeNode(op.operands)
	}
	return op.node
}

func (op *operation) Items(generator node.NodeGenerator) node.NodeItems {
	return newOperatorItems(generator, op)
}

func (op *operation) String() string {
	operands := op.operands
	if op.operator.processMethod == sequential {
		operands = operands[sequentialOffset:]
	}
	if len(operands) == 1 {
		return operands[0].iterator.String()
	}
	if op.formatting {
		return "<cycle>"
	}
	op.formatting = true
	result := node.Format(
		fmt.Sprintf(op.operator.template, formatOperands(op.operator.infix, operands)),
		op.Root(),
	)
	op.formatting = false
	return result
}

func (op *operation) fork(alternate node.NodeIterator) *operation {
	alternate = op.substitute(0, alternate)
	exit := op.slice(1, len(op.operands))
	return &operation{
		operator:   orOperator,
		operands:   []node.NodeIterator{alternate, exit},
		generators: op.generators[0:2],
	}
}

// Return a slice of operands from [start:end].
func (op *operation) slice(start int, end int) node.NodeIterator {
	if end-start == 1 {
		return op.operands[start]
	}
	return op.sliceCopy(start, end)
}

func (op *operation) sliceCopy(start int, end int) *operation {
	operands := make([]node.NodeIterator, end-start)
	copy(operands, op.operands[start:end])
	generators := make([]node.NodeGenerator, end-start)
	copy(generators, op.generators[start:end])
	return &operation{
		operator:   op.operator,
		operands:   operands,
		generators: generators,
	}
}

// Return a copy with `position` replaced with `item`.
func (op *operation) substitute(position int, item node.NodeIterator) *operation {
	result := op.sliceCopy(0, len(op.operands))
	result.operands[0] = item
	return result
}

func (op *operation) getGenerators(generator node.NodeGenerator) []node.NodeGenerator {
	if op.generators == nil {
		op.generators = make([]node.NodeGenerator, len(op.operands))
		for i := range op.operands {
			op.generators[i] = generator.ReserveNext()
		}
	}
	return op.generators
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

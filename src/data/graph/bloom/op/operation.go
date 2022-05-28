package op

import (
	"fmt"
	"strings"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type operation struct {
	operator         *operator
	operands         []node.NodeIterator
	generators       []node.NodeGenerator
	labels           []string
	metadataOperands []node.NodeMetadataProvider
	node             *node.Node
	formatting       bool // Used to detect cycles during formatting.
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
	if op.formatting {
		return "<cycle>"
	}
	op.formatting = true
	result := node.Format(
		fmt.Sprintf(op.operator.template, formatOperands(op.operator.infix, op.operands)),
		op.Root(),
	)
	op.formatting = false
	return result
}

func (op *operation) Header() query.QueryRowHeader {
	return op
}

func (op *operation) Labels() []string {
	if op.labels == nil {
		op.metadataOperands = make([]node.NodeMetadataProvider, 0, len(op.operands))
		op.labels = make([]string, 0, len(op.operands))
		for _, operand := range op.operands {
			metadataOperand, hasMetadata := operand.(node.NodeMetadataProvider)
			headerOperand, hasHeader := operand.(query.QueryRowHeader)
			if hasMetadata && hasHeader {
				op.metadataOperands = append(op.metadataOperands, metadataOperand)
				op.labels = append(op.labels, headerOperand.Labels()...)
			}
		}
	}
	return op.labels
}

func (op *operation) Metadata(paths []string, items []node.NodeItems) node.NodeMetadata {
	if len(op.Labels()) == 0 {
		return nil
	}
	result := make([]*weight.WeightedString, 0, len(op.Labels()))
	for _, operand := range op.metadataOperands {
		result = append(result, operand.Metadata(paths, items)...)
	}
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

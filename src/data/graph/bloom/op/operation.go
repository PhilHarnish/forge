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
	labels           []string
	metadataOperands []node.NodeMetadataProvider
	node             *node.Node
	formatting       bool
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

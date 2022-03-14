package op

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/null"
	"github.com/philharnish/forge/src/data/graph/bloom/span"
)

func And(operands ...node.NodeIterator) node.NodeIterator {
	if len(operands) == 0 {
		return null.Null
	} else if len(operands) == 1 {
		return operands[0]
	}
	return flatOperation(andOperator, operands)
}

func Or(operands ...node.NodeIterator) node.NodeIterator {
	if len(operands) == 0 {
		return null.Null
	} else if len(operands) == 1 {
		return operands[0]
	}
	return flatOperation(orOperator, operands)
}

func Concat(operands ...node.NodeIterator) node.NodeIterator {
	if len(operands) == 0 {
		return null.Null
	} else if len(operands) == 1 {
		return operands[0]
	}
	return flatOperation(concatOperator, operands)
}

func Join(separator string, operands ...node.NodeIterator) node.NodeIterator {
	if len(operands) == 0 {
		return null.Null
	} else if len(operands) == 1 {
		return operands[0]
	} else if separator == "" {
		return Concat(operands...)
	}
	concatOperands := make([]node.NodeIterator, len(operands))
	concatOperands[0] = operands[0]
	for i, operand := range operands[1:] {
		concatOperands[i+1] = span.NewSpan(separator, operand)
	}
	return Concat(concatOperands...)
}

func flatOperation(op *operator, operands []node.NodeIterator) *operation {
	return &operation{
		operator: op,
		operands: flatten(op, operands),
	}
}

func flatten(op *operator, operands []node.NodeIterator) []node.NodeIterator {
	newBufferSize := 0
	shouldMerge := false
	for _, operand := range operands {
		asOperation, matches := operand.(*operation)
		if !matches || asOperation.operator != op {
			newBufferSize++ // We would directly copy in this case.
			continue
		}
		newBufferSize += len(asOperation.operands)
		shouldMerge = true
	}
	if !shouldMerge {
		return operands
	}
	mergedOperands := make([]node.NodeIterator, 0, newBufferSize)
	for _, operand := range operands {
		asOperation, matches := operand.(*operation)
		if !matches || asOperation.operator != op {
			mergedOperands = append(mergedOperands, operand)
			continue
		}
		mergedOperands = append(mergedOperands, asOperation.operands...)
	}
	return mergedOperands
}

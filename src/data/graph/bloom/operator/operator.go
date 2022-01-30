package operator

import (
	"fmt"
	"strings"
)

type Operator interface {
	String(operands []string) string
}

var And = &operator{
	template: "AND(%s)",
}

var Or = &operator{
	template: "OR(%s)",
}

var Concat = &operator{
	template: "CONCAT(%s)",
}

var JoinWithSpace = &operator{
	template: "JOIN(' ', %s)",
}

type operator struct {
	template string
}

func (operator *operator) String(operands []string) string {
	body := strings.Join(operands, ", ")
	return fmt.Sprintf(operator.template, body)
}

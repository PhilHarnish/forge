package operator

import (
	"fmt"
	"strings"
)

type Operator interface {
	String() string
}

var And = operator{
	template: "(%s)",
	infix:    " && ",
}

var Or = operator{
	template: "(%s)",
	infix:    " || ",
}

type operator struct {
	template string
	infix    string
}

func (operator *operator) String(operands ...interface{}) string {
	formatted := make([]string, len(operands))
	for i, operand := range operands {
		formatted[i] = fmt.Sprint(operand)
	}
	body := strings.Join(formatted, operator.infix)
	return fmt.Sprintf(operator.template, body)
}

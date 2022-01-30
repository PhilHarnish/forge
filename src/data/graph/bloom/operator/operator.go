package operator

import (
	"fmt"
	"strings"
)

type Operator interface {
	String(operands []string) string
}

var And = &operator{
	template: "(%s)",
	infix:    " && ",
}

var Or = &operator{
	template: "(%s)",
	infix:    " || ",
}

var Concat = &operator{
	template: "(%s)",
	infix:    " + ",
}

var JoinWithSpace = &operator{
	template: "JOIN(' ', %s)",
	infix:    ", ",
}

type operator struct {
	template string
	infix    string
}

func (operator *operator) String(operands []string) string {
	body := strings.Join(operands, operator.infix)
	return fmt.Sprintf(operator.template, body)
}

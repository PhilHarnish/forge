package op

type operator struct {
	template string
}

var andOperator = &operator{
	template: "AND(%s)",
}

var orOperator = &operator{
	template: "OR(%s)",
}

var concatOperator = &operator{
	template: "CONCAT(%s)",
}

var joinOperator = &operator{
	template: "JOIN('%s', %s)",
}
